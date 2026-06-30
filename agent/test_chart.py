"""
图表生成功能测试示例
"""
import asyncio
from app.core.chart_processor import chart_detector, chart_generator


def test_chart_detection():
    """测试图表检测功能"""
    print("=" * 60)
    print("测试1: 图表检测")
    print("=" * 60)
    
    test_cases = [
        "请用图表展示最近5个月的销售数据",
        "用柱状图对比各部门业绩",
        "画出温度变化趋势的折线图",
        "用饼图展示市场份额分布",
        "帮我分析一下用户数据",  # 无图表请求
        "绘制一个雷达图展示能力评估",
        "用echarts生成散点图",
        "显示销售数据的可视化图表"
    ]
    
    for text in test_cases:
        is_chart, chart_type, description = chart_detector.detect_chart_request(text)
        print(f"\n输入: {text}")
        print(f"  - 是否图表请求: {is_chart}")
        print(f"  - 图表类型: {chart_type}")
        print(f"  - 数据描述: {description}")


def test_chart_generation():
    """测试图表生成功能"""
    print("\n" + "=" * 60)
    print("测试2: 图表生成")
    print("=" * 60)
    
    test_cases = [
        {
            "chart_type": "bar",
            "description": "各部门销售额对比",
            "response": "研发部销售额120万，市场部150万，销售部180万，人事部50万"
        },
        {
            "chart_type": "line",
            "description": "月度温度变化趋势",
            "response": "1月温度5度，2月温度8度，3月温度15度，4月温度20度，5月温度25度"
        },
        {
            "chart_type": "pie",
            "description": "产品销售占比",
            "response": "产品A销售335件，产品B销售310件，产品C销售234件，产品D销售135件"
        },
        {
            "chart_type": "radar",
            "description": "员工能力评估",
            "response": "编程能力85分，沟通能力70分，学习能力90分，团队协作80分，创新能力75分"
        }
    ]
    
    for case in test_cases:
        print(f"\n生成{case['chart_type']}图表:")
        print(f"描述: {case['description']}")
        print(f"数据: {case['response']}")
        
        chart_markdown = chart_generator.generate_chart(
            chart_type=case['chart_type'],
            data_description=case['description'],
            raw_response=case['response']
        )
        
        print(f"\n生成的Markdown:\n{chart_markdown}\n")


def test_data_extraction():
    """测试数据提取功能"""
    print("\n" + "=" * 60)
    print("测试3: 数据提取")
    print("=" * 60)
    
    test_responses = [
        "销售额为120万元，同比增长15%",
        "1月:100, 2月:150, 3月:200, 4月:180, 5月:220",
        "研发部50人，市场部30人，销售部40人",
        "温度从20度上升到25度，湿度从60%下降到50%"
    ]
    
    for response in test_responses:
        data = chart_generator._extract_data_from_response(response)
        print(f"\n原始文本: {response}")
        print(f"提取数据: {data}")


def test_chart_type_inference():
    """测试图表类型推断"""
    print("\n" + "=" * 60)
    print("测试4: 图表类型推断")
    print("=" * 60)
    
    test_cases = [
        "对比一下各部门的业绩",
        "展示销售额的变化趋势",
        "分析市场份额的分布情况",
        "评估员工的能力雷达图"
    ]
    
    for text in test_cases:
        is_chart, chart_type, description = chart_detector.detect_chart_request(text)
        print(f"\n输入: {text}")
        print(f"推断类型: {chart_type}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("图表生成功能测试套件")
    print("=" * 60)
    
    test_chart_detection()
    test_chart_generation()
    test_data_extraction()
    test_chart_type_inference()
    
    print("\n" + "=" * 60)
    print("所有测试完成!")
    print("=" * 60)
