import httpx
from typing import Dict, List, Optional, Any
from loguru import logger
import json

from config import settings
from app.services.mcp_tools import mcp_tools_service


class MCPService:
    def __init__(self):
        self.server_url = settings.mcp_server_url
        self.timeout = settings.mcp_timeout
        self._client: Optional[httpx.AsyncClient] = None
        # 只有当 server_url 有效时才使用外部服务
        self.use_local_tools = not self.server_url or self.server_url == "http://localhost:3000"
        logger.info(f"MCP service initialized (use_local_tools={self.use_local_tools})")
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用 MCP 工具"""
        # 优先使用本地工具
        if self.use_local_tools:
            logger.info(f"Using local MCP tool: {tool_name}")
            return await mcp_tools_service.call_tool(tool_name, parameters)
        
        # 使用外部 MCP 服务器
        if not self.server_url:
            logger.warning("MCP server URL not configured, falling back to local tools")
            return await mcp_tools_service.call_tool(tool_name, parameters)
        
        try:
            client = await self._get_client()
            
            response = await client.post(
                f"{self.server_url}/tools/{tool_name}",
                json=parameters
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"External MCP tool {tool_name} called successfully")
            return result
        except httpx.HTTPError as e:
            logger.error(f"External MCP tool call error: {str(e)}, falling back to local tools")
            # 降级到本地工具
            return await mcp_tools_service.call_tool(tool_name, parameters)
        except Exception as e:
            logger.error(f"Unexpected MCP error: {str(e)}, falling back to local tools")
            return await mcp_tools_service.call_tool(tool_name, parameters)
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """列出可用工具"""
        # 优先使用本地工具
        if self.use_local_tools:
            tools_dict = mcp_tools_service.list_tools()
            return [
                {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"]
                }
                for name, info in tools_dict.items()
            ]
        
        # 使用外部 MCP 服务器
        if not self.server_url:
            logger.warning("MCP server URL not configured, using local tools")
            tools_dict = mcp_tools_service.list_tools()
            return [
                {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"]
                }
                for name, info in tools_dict.items()
            ]
        
        try:
            client = await self._get_client()
            
            response = await client.get(f"{self.server_url}/tools")
            response.raise_for_status()
            
            tools = response.json()
            logger.info(f"Retrieved {len(tools)} external MCP tools")
            return tools
        except Exception as e:
            logger.error(f"Error listing external MCP tools: {str(e)}, using local tools")
            tools_dict = mcp_tools_service.list_tools()
            return [
                {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"]
                }
                for name, info in tools_dict.items()
            ]
    
    async def close(self):
        """关闭客户端连接"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


mcp_service = MCPService()
