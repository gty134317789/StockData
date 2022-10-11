# 沪深A股各公司股价爬取与可视化

## 概要

​        A股向来跟跌不跟涨，实在是有点受不了，正好最近学了点ETL的操作，自己又有点爬虫的基础，就准备自己做一个玩玩，顺便交了学校的大作业。总的来说就是做了一套1.0版本的ETL。之后对Hadoop2.7.x套件熟悉了，再上2.0版本。

---

## 工具和技术栈

- Python——获取数据
- Kettle——ETL操作
- ElastSearch套件(Kibana+Logstash)——可视化

---

## 过程

### 1.获取数据

​        在网上找到了东方财富的接口(http://quote.eastmoney.com/center/gridlist.html#hs_a_board)写个爬虫把数据爬下来，先存到csv里面，写入本地的。有两个比较主要的函数：

1. get_stock_names()——获取股票的名字，爬一页放到txt里面；
2. get_data()——获取到股票的名字，先做个预处理，比如沪深市代码前面用0和1区分等等，然后写入csv。

![image text](https://github.com/gty134317789/StockData/blob/main/image/image-20221011110346043.png)

### 2.ETL

​        这一步主要就是用Kettle去做了，很方便，直接把csv导入MySQL。在这一步也试着用DataX实现了相同的功能，但是感觉还是Kettle方便一点。而且Kettle排序去重方便多了，但是鉴于股票这个东西，最好还是按照时间序列来分析，就没去除非法值，用0替代。

![image text](https://github.com/gty134317789/StockData/blob/main/image/image-20221011110555362.png)

### 3.可视化

​        这一步蛮搞的，Kibana必须得配置好，不然服务起不来。

​		自己定义一个Logstash.conf，用的标准输入输出，配置一下。

```shell
input {
	file {
		path => ["E:/PycharmProjects/BigDataSight/stockdata/000695.csv"]
		start_position => "beginning"
		sincedb_path => "NULL"
	}
}

filter {
	 csv {
		separator => ","
		columns =>
		["日期","股票代码","名称","收盘价","最高价","最低价","开盘价","前收盘","涨跌额","涨跌幅","换手率","成交量","成交金额","总市值","流通市值"]
	}
	mutate {
		convert => {
			"日期" => "string"
	 		"股票代码" => "string"
	 		"名称" => "string"
	 		"收盘价" => "float"
			"最高价" => "float"
			"最低价" => "float"
			"开盘价" => "float"
			"前收盘" => "float"
			"涨跌额" => "float"
			"涨跌幅" => "float"
			"换手率" => "float"
			"成交量" => "float"
			"成交金额" => "float"
			"总市值" => "float"
			"流通市值"=>"float"
		}
	}

}

output{
	elasticsearch {      
		hosts => ["localhost:9200"]
		index => "stocksight"
		document_type => "stocksight"
	}
	
	stdout{}
	
}
```

​		然后去Kibana里面检查数据、创建索引，再简单看下可视化的效果。

![image text](https://github.com/gty134317789/StockData/blob/main/image/image-20221011111024871.png)

---

## 总结

​		基本就是熟悉了一下1.0版本的ETL的过程，熟悉一下主要的技术栈。但感觉还是很不够的，现在都在转Hadoop套件，以后还是多用Hadoop套件吧。

