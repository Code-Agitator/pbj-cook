# Cowjiang AdGuard

自建 DNS 广告过滤系统：基于 AdGuard Home + 自有云服务器，为 iOS / Android / 全屋设备提供广告与追踪拦截。

- iOS：安装 [Cowjiang-AdGuard.mobileconfig](https://github.com/Cowjiang/cowjiang-adguard/releases/download/profile/Cowjiang-AdGuard.mobileconfig) 描述文件（加密 DNS DoT，蜂窝/Wi-Fi 全局生效）
- Android：设置 → 网络 → 私人 DNS → 填入 `dns.inceptae.com`
- 家庭路由器 / 其他设备：DNS 填服务器 IP（明文 53）

## 数据来源与处理链路

每日自动从 [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules) 拉取最新的 `sr_reject_list.module`（约 19 万条拦截规则），加上本仓库人工维护的 `custom_reject_list.module`，由 `factory/build_agh.sh` 转换为 AdGuard DNS 过滤语法：

| 生成物 | 用途 | AGH 订阅地址 |
|---|---|---|
| `agh_sr_reject.txt` | 上游全量拦截列表 | `raw.githubusercontent.com/<你>/<新仓库>/master/agh_sr_reject.txt` |
| `agh_custom_reject.txt` | 自定义拦截规则 | `raw.githubusercontent.com/<你>/<新仓库>/master/agh_custom_reject.txt` |
| `Cowjiang-AdGuard.mobileconfig` | iOS 描述文件 | [Release 下载](https://github.com/Cowjiang/cowjiang-adguard/releases/download/profile/Cowjiang-AdGuard.mobileconfig) |

## 仓库结构

```
├── custom_reject_list.module      # 人工维护的自定义拦截规则 (Shadowrocket 语法)
├── sr_reject_list.module          # 每日自动从上游拉取 (CI 生成, 勿手改)
├── factory/build_agh.sh           # 语法转换 + 描述文件生成
└── .github/workflows/
    ├── build.yml                  # 每日: 拉上游 → 转换 → 提交 → 更新 Release
    └── renew-cert.yml             # 双月: 签发/部署 dns.inceptae.com 证书
```

## 规则语法映射

```
DOMAIN,x,REJECT        →  ||x^
DOMAIN-SUFFIX,x,REJECT →  ||x^
DOMAIN-KEYWORD,x       →  x        (子串匹配)
IP-CIDR                →  (跳过, DNS 层无法按 IP 拦截)
```
