from typing import List, Dict, AsyncIterator, Optional
from app.core.llm import llm_service
from app.services.knowledge_service import knowledge_service
from app.services.mcp_service import mcp_service
from app.services.conversation_service import conversation_service
from loguru import logger
import re
import json
from config import settings


class Agent:
    def __init__(self):
        self.system_prompt = """你是一个企业级智能助手，具有以下能力：
1. 可以回答用户的各种问题
2. 可以检索企业知识库获取相关信息
3. 可以调用外部工具（通过 MCP）执行任务

当需要调用工具时，请使用以下格式：
TOOL_CALL: tool_name|param1=value1|param2=value2

请以专业、准确、友好的方式回答用户问题。如果不确定答案，请诚实地说明。"""
        
        # 对话摘要提示
        self.summary_prompt = """请将以下对话内容总结为一个简洁的摘要，保留关键信息和上下文，以便后续对话能够基于这个摘要继续进行。"""
    
    async def _summarize_conversation(self, messages: List[Dict[str, str]]) -> str:
        """生成对话摘要"""
        if not messages:
            return ""
        
        try:
            # 构建摘要请求
            summary_messages = [
                {"role": "system", "content": self.summary_prompt},
                {"role": "user", "content": f"对话内容：\n{json.dumps(messages, ensure_ascii=False)}"}
            ]
            
            summary = await llm_service.chat(
                messages=summary_messages,
                system_prompt=self.summary_prompt
            )
            
            logger.info(f"Generated conversation summary: {len(summary)} chars")
            return summary
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return ""
    
    def _truncate_messages(
        self,
        messages: List[Dict[str, str]],
        max_history: int
    ) -> List[Dict[str, str]]:
        """截断消息历史（滑动窗口）"""
        if len(messages) <= max_history:
            return messages
        
        # 保留系统消息和最近的消息
        system_messages = [m for m in messages if m["role"] == "system"]
        recent_messages = messages[-max_history:]
        
        return system_messages + recent_messages
    
    def _parse_tool_calls(self, text: str) -> List[Dict]:
        """解析工具调用"""
        pattern = r'TOOL_CALL:\s*(\w+)\|(.*)'
        matches = re.findall(pattern, text)
        
        tool_calls = []
        for match in matches:
            tool_name = match[0]
            params_str = match[1]
            
            params = {}
            if params_str:
                for param in params_str.split('|'):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key.strip()] = value.strip()
            
            tool_calls.append({
                "tool_name": tool_name,
                "parameters": params
            })
        
        return tool_calls
    
    async def _execute_tool_calls(self, tool_calls: List[Dict]) -> str:
        """执行工具调用"""
        results = []
        for call in tool_calls:
            result = await mcp_service.call_tool(
                tool_name=call["tool_name"],
                parameters=call["parameters"]
            )
            results.append(f"工具 {call['tool_name']} 的结果: {json.dumps(result, ensure_ascii=False)}")
        
        return "\n\n".join(results)
    
    async def process(
        self,
        messages: List[Dict[str, str]],
        use_knowledge: bool = True,
        use_mcp: bool = True,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> str:
        """处理用户消息（非流式）"""
        user_message = messages[-1]["content"] if messages else ""
        
        # 处理长对话
        if settings.enable_conversation_summary:
            # 如果消息数量超过阈值，生成摘要
            if len(messages) > settings.summary_threshold:
                summary = await self._summarize_conversation(messages)
                if summary and conversation_id:
                    await conversation_service.update_summary(conversation_id, summary)
                
                # 使用滑动窗口截断消息
                messages = self._truncate_messages(messages, settings.max_conversation_history)
            else:
                # 直接截断
                messages = self._truncate_messages(messages, settings.max_conversation_history)
        else:
            messages = self._truncate_messages(messages, settings.max_conversation_history)
        
        # 知识库检索
        context = ""
        if use_knowledge and user_message:
            context = await knowledge_service.search(user_message, top_k=3)
        
        # 构建增强的系统提示
        enhanced_system = self.system_prompt
        if context:
            enhanced_system += f"\n\n相关知识库内容：\n{context}"
        
        # 第一轮：调用 LLM
        response = await llm_service.chat(
            messages=messages,
            system_prompt=enhanced_system,
            model=model
        )
        
        # 检查是否有工具调用
        if use_mcp:
            tool_calls = self._parse_tool_calls(response)
            if tool_calls:
                # 执行工具调用
                tool_results = await self._execute_tool_calls(tool_calls)
                
                # 将工具结果加入对话历史
                messages.append({"role": "assistant", "content": response})
                messages.append({"role": "user", "content": f"工具执行结果：\n{tool_results}\n\n请基于工具结果回答用户问题。"})
                
                # 第二轮：基于工具结果生成最终回答
                response = await llm_service.chat(
                    messages=messages,
                    system_prompt=enhanced_system,
                    model=model
                )
        
        return response
    
    async def process_stream(
        self,
        messages: List[Dict[str, str]],
        use_knowledge: bool = True,
        use_mcp: bool = True,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        model: Optional[str] = None
    ) -> AsyncIterator[str]:
        """处理用户消息（流式）"""
        user_message = messages[-1]["content"] if messages else ""
        
        # 处理长对话
        if settings.enable_conversation_summary:
            if len(messages) > settings.summary_threshold:
                summary = await self._summarize_conversation(messages)
                if summary and conversation_id:
                    await conversation_service.update_summary(conversation_id, summary)
                messages = self._truncate_messages(messages, settings.max_conversation_history)
            else:
                messages = self._truncate_messages(messages, settings.max_conversation_history)
        else:
            messages = self._truncate_messages(messages, settings.max_conversation_history)
        
        # 知识库检索
        context = ""
        if use_knowledge and user_message:
            context = await knowledge_service.search(user_message, top_k=3)
        
        # 构建增强的系统提示
        enhanced_system = self.system_prompt
        if context:
            enhanced_system += f"\n\n相关知识库内容：\n{context}"
        
        # 第一轮：流式调用 LLM
        full_response = ""
        async for chunk in llm_service.chat_stream(
            messages=messages,
            system_prompt=enhanced_system,
            model=model
        ):
            full_response += chunk
            yield chunk
        
        # 检查是否有工具调用（流式响应结束后处理）
        if use_mcp:
            tool_calls = self._parse_tool_calls(full_response)
            if tool_calls:
                # 执行工具调用
                tool_results = await self._execute_tool_calls(tool_calls)
                
                # 将工具结果加入对话历史
                messages.append({"role": "assistant", "content": full_response})
                messages.append({"role": "user", "content": f"工具执行结果：\n{tool_results}\n\n请基于工具结果回答用户问题。"})
                
                # 第二轮：基于工具结果生成最终回答（流式）
                async for chunk in llm_service.chat_stream(
                    messages=messages,
                    system_prompt=enhanced_system,
                    model=model
                ):
                    yield chunk


agent = Agent()
