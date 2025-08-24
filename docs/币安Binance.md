### API基本信息

- 本篇列出接口的 base URL 有:
    - **[https://api.binance.com](https://api.binance.com/)**
    - **[https://api-gcp.binance.com](https://api-gcp.binance.com/)**
    - **[https://api1.binance.com](https://api1.binance.com/)**
    - **[https://api2.binance.com](https://api2.binance.com/)**
    - **[https://api3.binance.com](https://api3.binance.com/)**
    - **[https://api4.binance.com](https://api4.binance.com/)**
- 无需鉴权，仅获取公共数据 [https://data-api.binance.vision](https://data-api.binance.vision)
- 上述列表的最后4个接口 (`api1`-`api4`) 会提供更好的性能，但其稳定性略为逊色。因此，请务必使用最适合的URL。
- 响应默认为 JSON 格式。如果您想接收 SBE 格式的响应，请参考 [简单二进制编码 （SBE） 常见问题](https://developers.binance.com/docs/zh-CN/binance-spot-api-docs/faqs/sbe_faq)。
- 除非另有说明，否则数据将按**时间顺序**返回。
    - 如果未指定 `startTime` 或 `endTime`，则返回最近的条目，直至达到限制值。
    - 如果指定 `startTime`，则返回从 `startTime` 到限制值为止最老的条目。
    - 如果指定 `endTime`，则返回截至 `endTime` 和限制值为止最近的条目。
    - 如果同时指定 `startTime` 和 `endTime`，则行为类似于 `startTime`，但不超过 `endTime`。
- JSON 响应中的所有时间和时间戳相关字段均以**毫秒为默认单位**。要以微秒为单位接收信息，请添加报文头 `X-MBX-TIME-UNIT：MICROSECOND` 或 `X-MBX-TIME-UNIT：microsecond`。
- 我们支持 HMAC，RSA 以及 Ed25519 Key 类型。 如需进一步了解，请参考 [API Key 类型](https://developers.binance.com/docs/zh-CN/binance-spot-api-docs/faqs/api_key_types)。
- 时间戳参数（例如 `startTime`、`endTime`、`timestamp`）可以以毫秒或微秒为单位传递。
- 对于仅发送公开市场数据的 API，您可以使用接口的 base URL [https://data-api.binance.vision](https://data-api.binance.vision/) 。请参考 [Market Data Only_CN](https://developers.binance.com/docs/zh-CN/binance-spot-api-docs/faqs/market_data_only) 页面。
- 如需进一步了解枚举或术语，请参考 [现货交易API术语表](https://developers.binance.com/docs/zh-CN/binance-spot-api-docs/faqs/spot_glossary) 页面。
- API 处理请求的超时时间为 10 秒。如果撮合引擎的响应时间超过此时间，API 将返回 “Timeout waiting for response from backend server. Send status unknown; execution status unknown.”。[(-1007 超时)](https://developers.binance.com/docs/zh-CN/binance-spot-api-docs/errors#-1007-timeout)
    - 这并不总是意味着该请求在撮合引擎中失败。
    - 如果请求状态未显示在 [WebSocket 账户接口](https://developers.binance.com/docs/zh-CN/binance-spot-api-docs/user-data-stream) 中，请执行 API 查询以获取其状态。

### K线数据

```
GET /api/v3/klines
```

每根K线的开盘时间可视为唯一ID

**权重:** 2

**参数:** 

| 名称        | 类型     | 是否必需 | 描述                   |
| --------- | ------ | ---- | -------------------- |
| symbol    | STRING | YES  |                      |
| interval  | ENUM   | YES  | 请参考 [`K线间隔`](#K线间隔)  |
| startTime | LONG   | NO   |                      |
| endTime   | LONG   | NO   |                      |
| timeZone  | STRING | NO   | 默认值： 0 (UTC)         |
| limit     | INT    | NO   | 默认值： 500； 最大值： 1000。 |

### K线间隔

支持的K线间隔 （区分大小写）：

|间隔|`间隔` 值|
|---|---|
|seconds -> 秒|`1s`|
|minutes -> 分钟|`1m`， `3m`， `5m`， `15m`， `30m`|
|hours -> 小时|`1h`， `2h`， `4h`， `6h`， `8h`， `12h`|
|days -> 天|`1d`， `3d`|
|weeks -> 周|`1w`|
|months -> 月|`1M`|

**请注意：**

- 如果未发送`startTime`和`endTime`，将返回最近的K线数据。
- `timeZone`支持的值包括：
    - 小时和分钟（例如 `-1:00`，`05:45`）
    - 仅小时（例如 `0`，`8`，`4`）
    - 接受的值范围严格为 [-12:00 到 +14:00]（包括边界）
- 如果提供了`timeZone`，K线间隔将在该时区中解释，而不是在UTC中。
- 请注意，无论`timeZone`如何，`startTime`和`endTime`始终以UTC时区解释。

**数据源:** 数据库

**响应:** 

```
[
  [
    1499040000000,      // 开盘时间
    "0.01634790",       // 开盘价
    "0.80000000",       // 最高价
    "0.01575800",       // 最低价
    "0.01577100",       // 收盘价(当前K线未结束的即为最新价)
    "148976.11427815",  // 成交量
    1499644799999,      // 收盘时间
    "2434.19055334",    // 成交额
    308,                // 成交笔数
    "1756.87402397",    // 主动买入成交量
    "28.46694368",      // 主动买入成交额
    "17928899.62484339" // 请忽略该参数
  ]
]
```

### HTTP错误码

- HTTP `4XX` 错误码用于指示错误的请求内容、行为、格式。问题在于请求者。
- HTTP `403` 错误码表示违反WAF限制(Web应用程序防火墙)。
- HTTP `409` 错误码表示重新下单(cancelReplace)的请求部分成功。(比如取消订单失败，但是下单成功了)
- HTTP `429` 错误码表示警告访问频次超限，即将被封IP。
- HTTP `418` 表示收到429后继续访问，于是被封了。
- HTTP `5XX` 错误码用于指示Binance服务侧的问题。

### 速率限制

```
"rateLimits":[
{"rateLimitType":"REQUEST_WEIGHT","interval":"MINUTE","intervalNum":1,"limit":6000},{"rateLimitType":"ORDERS","interval":"SECOND","intervalNum":10,"limit":100},{"rateLimitType":"ORDERS","interval":"DAY","intervalNum":1,"limit":200000},{"rateLimitType":"RAW_REQUESTS","interval":"MINUTE","intervalNum":5,"limit":61000}
]
```

每分钟请求权重6000，也就是每分钟可请求秒级K线3000次(K线请求权重为2)，长度限制最长1000，一个IP每分钟只能获取大约1月时间长度秒K

可以写个程序慢慢拉以前的数据到本地，自己维护一个K线数据