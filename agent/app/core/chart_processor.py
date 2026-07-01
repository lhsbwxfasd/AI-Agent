import re
import json
from typing import Dict, Optional, List, Tuple
from loguru import logger


class ChartDetector:
    """图表请求检测器"""
    
    def __init__(self):
        self.chart_keywords = [
            '图表', '图形', '图', 'chart', 'graph', 'plot',
            'echart', 'echarts', '可视化', '绘制', '画图',
            '柱状图', '折线图', '饼图', '散点图', '雷达图',
            '条形图', '线图', '圆饼图', '扇形图',
            '对比图', '趋势图', '分布图', '统计图'
        ]
        
        self.chart_type_mapping = {
            '柱状图': 'bar', '条形图': 'bar', '柱图': 'bar',
            '折线图': 'line', '线图': 'line', '趋势图': 'line',
            '饼图': 'pie', '圆饼图': 'pie', '扇形图': 'pie',
            '散点图': 'scatter', '点图': 'scatter',
            '雷达图': 'radar',
            '仪表盘': 'gauge'
        }
        
        self.data_keywords = [
            '数据', '统计', '分析', '对比', '趋势', '分布',
            '销量', '销售额', '收入', '支出', '利润',
            '温度', '湿度', '速度', '数量', '人数',
            '百分比', '占比', '比例', '增长率'
        ]
    
    def detect_chart_request(self, text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        检测是否包含图表请求
        
        返回: (是否请求图表, 图表类型, 提取的数据描述)
        """
        text_lower = text.lower()
        
        # 排除附件图片相关的问题（不是要生成图表）
        exclude_keywords = [
            '附件图', '上传图', '图片', '图像', '截图', '照片',
            '识别图', '提取图', '解析图', '分析图', '看图',
            '图片中', '图像中', '图中', '照片中',
            'attachment', 'image', 'photo', 'picture'
        ]
        
        # 如果包含排除关键词，说明不是要生成图表
        if any(keyword in text_lower for keyword in exclude_keywords):
            return False, None, None
        
        has_chart_keyword = any(keyword in text_lower for keyword in self.chart_keywords)
        
        if not has_chart_keyword:
            return False, None, None
        
        chart_type = None
        for cn_type, en_type in self.chart_type_mapping.items():
            if cn_type in text:
                chart_type = en_type
                break
        
        if not chart_type:
            if any(word in text_lower for word in ['对比', '比较', '柱', '条']):
                chart_type = 'bar'
            elif any(word in text_lower for word in ['趋势', '变化', '折线', '线']):
                chart_type = 'line'
            elif any(word in text_lower for word in ['占比', '分布', '饼', '扇形']):
                chart_type = 'pie'
            else:
                chart_type = 'bar'
        
        data_description = self._extract_data_description(text)
        
        logger.info(f"Detected chart request: type={chart_type}, description={data_description}")
        return True, chart_type, data_description
    
    def _extract_data_description(self, text: str) -> str:
        """提取数据描述"""
        patterns = [
            r'(?:展示|显示|绘制|画出?|生成).{0,20}?(?:图表|图形|图)',
            r'(.{0,30}?).{0,5}?(?:的|之)?(?:图表|图形|图|趋势|分布|对比)',
            r'(?:分析|统计).{0,20}?(?:数据|信息)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return text


class ChartGenerator:
    """ECharts图表生成器"""
    
    def __init__(self):
        self.color_palette = [
            '#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399',
            '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de'
        ]
    
    def generate_chart(
        self,
        chart_type: str,
        data_description: str,
        raw_response: str
    ) -> str:
        """
        生成ECharts图表配置
        
        返回: Markdown格式的ECharts代码块
        """
        try:
            extracted_data = self._extract_data_from_response(raw_response)
            
            if chart_type == 'bar':
                option = self._generate_bar_chart(extracted_data, data_description)
            elif chart_type == 'line':
                option = self._generate_line_chart(extracted_data, data_description)
            elif chart_type == 'pie':
                option = self._generate_pie_chart(extracted_data, data_description)
            elif chart_type == 'scatter':
                option = self._generate_scatter_chart(extracted_data, data_description)
            elif chart_type == 'radar':
                option = self._generate_radar_chart(extracted_data, data_description)
            else:
                option = self._generate_bar_chart(extracted_data, data_description)
            
            chart_json = json.dumps(option, ensure_ascii=False, indent=2)
            
            return f"```echarts\n{chart_json}\n```"
            
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            return ""
    
    def _extract_data_from_response(self, response: str) -> Dict:
        """从AI响应中提取数据"""
        numbers = re.findall(r'\d+\.?\d*', response)
        
        categories = re.findall(r'[一二三四五六七八九十\d]+[月日周]|[周月年][一二三四五六七八九十\d]+|\d{4}年', response)
        
        if not categories:
            categories = ['数据1', '数据2', '数据3', '数据4', '数据5']
        
        if not numbers:
            numbers = [10, 20, 30, 40, 50]
        else:
            numbers = [float(n) for n in numbers[:len(categories)]]
        
        return {
            'categories': categories[:len(numbers)],
            'values': numbers
        }
    
    def _generate_bar_chart(self, data: Dict, description: str) -> Dict:
        """生成柱状图配置"""
        return {
            "title": {
                "text": description[:30] if description else "数据统计",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "shadow"
                }
            },
            "xAxis": {
                "type": "category",
                "data": data['categories']
            },
            "yAxis": {
                "type": "value"
            },
            "series": [{
                "type": "bar",
                "data": data['values'],
                "itemStyle": {
                    "color": self.color_palette[0]
                },
                "emphasis": {
                    "itemStyle": {
                        "color": self.color_palette[1]
                    }
                }
            }]
        }
    
    def _generate_line_chart(self, data: Dict, description: str) -> Dict:
        """生成折线图配置"""
        return {
            "title": {
                "text": description[:30] if description else "趋势分析",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis"
            },
            "xAxis": {
                "type": "category",
                "data": data['categories'],
                "boundaryGap": False
            },
            "yAxis": {
                "type": "value"
            },
            "series": [{
                "type": "line",
                "data": data['values'],
                "smooth": True,
                "itemStyle": {
                    "color": self.color_palette[0]
                },
                "areaStyle": {
                    "color": {
                        "type": "linear",
                        "x": 0,
                        "y": 0,
                        "x2": 0,
                        "y2": 1,
                        "colorStops": [
                            {"offset": 0, "color": "rgba(64, 158, 255, 0.3)"},
                            {"offset": 1, "color": "rgba(64, 158, 255, 0.05)"}
                        ]
                    }
                }
            }]
        }
    
    def _generate_pie_chart(self, data: Dict, description: str) -> Dict:
        """生成饼图配置"""
        pie_data = []
        for i, (cat, val) in enumerate(zip(data['categories'], data['values'])):
            pie_data.append({
                "name": cat,
                "value": val
            })
        
        return {
            "title": {
                "text": description[:30] if description else "数据分布",
                "left": "center"
            },
            "tooltip": {
                "trigger": "item",
                "formatter": "{a} <br/>{b}: {c} ({d}%)"
            },
            "legend": {
                "orient": "vertical",
                "left": "left",
                "top": "middle"
            },
            "series": [{
                "name": "数据",
                "type": "pie",
                "radius": "50%",
                "center": ["60%", "50%"],
                "data": pie_data,
                "emphasis": {
                    "itemStyle": {
                        "shadowBlur": 10,
                        "shadowOffsetX": 0,
                        "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }
            }]
        }
    
    def _generate_scatter_chart(self, data: Dict, description: str) -> Dict:
        """生成散点图配置"""
        scatter_data = [[i, val] for i, val in enumerate(data['values'])]
        
        return {
            "title": {
                "text": description[:30] if description else "散点分布",
                "left": "center"
            },
            "tooltip": {
                "trigger": "item"
            },
            "xAxis": {
                "type": "value"
            },
            "yAxis": {
                "type": "value"
            },
            "series": [{
                "type": "scatter",
                "data": scatter_data,
                "symbolSize": 10,
                "itemStyle": {
                    "color": self.color_palette[0]
                }
            }]
        }
    
    def _generate_radar_chart(self, data: Dict, description: str) -> Dict:
        """生成雷达图配置"""
        max_value = max(data['values']) if data['values'] else 100
        
        indicator = []
        for cat in data['categories']:
            indicator.append({
                "name": cat,
                "max": max_value * 1.2
            })
        
        return {
            "title": {
                "text": description[:30] if description else "雷达分析",
                "left": "center"
            },
            "tooltip": {},
            "radar": {
                "indicator": indicator,
                "center": ["50%", "55%"],
                "radius": "65%"
            },
            "series": [{
                "name": "数据",
                "type": "radar",
                "data": [{
                    "value": data['values'],
                    "name": "数值",
                    "areaStyle": {
                        "color": "rgba(64, 158, 255, 0.3)"
                    }
                }]
            }]
        }


chart_detector = ChartDetector()
chart_generator = ChartGenerator()
