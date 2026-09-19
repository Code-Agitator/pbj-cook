# Cowjiang AdGuard

自建 DNS 广告过滤：AdGuard Home + 自有云服务器，iOS / Android / 全屋设备广告与追踪拦截。

- **iOS**：安装 [描述文件](https://github.com/Cowjiang/cowjiang-adguard/releases/download/profile/Cowjiang-AdGuard.mobileconfig)（DoT 加密 DNS，全局生效）
- **Android**：私人 DNS 填 DoT 域名
- **路由器 / 其他设备**：DNS 填服务器 IP

## 规则

每日自动拉取 [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules) 的拦截列表，与人工维护的 `rules/custom_reject_list.module` 合并，由 `factory/build_agh.sh` 转换为 AdGuard DNS 语法：

| 生成物（`dist/`，CI 生成勿手改） | AGH 订阅地址 |
|---|---|
| `agh_sr_reject.txt` | `raw.githubusercontent.com/Cowjiang/cowjiang-adguard/master/dist/agh_sr_reject.txt` |
| `agh_custom_reject.txt` | `raw.githubusercontent.com/Cowjiang/cowjiang-adguard/master/dist/agh_custom_reject.txt` |
| `Cowjiang-AdGuard.mobileconfig` | [Release 下载](https://github.com/Cowjiang/cowjiang-adguard/releases/download/profile/Cowjiang-AdGuard.mobileconfig) |

`upstream/` 为每日拉取的上游快照，`rules/` 为人工维护的源规则（Shadowrocket 语法），两者由 CI 每日更新/转换。

## 自动化

| Workflow | 触发 | 作用 |
|---|---|---|
| `build.yml` | 每日 + push master | 拉上游规则 → 转换 → 提交 `dist/` |
| `renew-cert.yml` | 双月 + 手动 | 续签证书 → 部署服务器 → 更新 Release 描述文件 |

证书由 Let's Encrypt 签发（acme.sh，DNS-01 验证），双月自动续期。签发与部署依赖 4 个 secrets（**Settings → Secrets and variables → Actions**）：

- `DNS_DOMAIN` — DoT 域名（如 `dns.example.com`）
- `CF_TOKEN` — Cloudflare API Token（Zone → DNS → Edit），用于 DNS-01 验证
- `SSH_HOST` — 服务器地址（SSH 连接目标，通常是公网 IP）
- `SSH_KEY` — 服务器 SSH 私钥

## License

GPL-3.0. Rule data is sourced daily from [GMOogway/shadowrocket-rules](https://github.com/GMOogway/shadowrocket-rules) (GPL-3.0); the converted lists in this repository are therefore distributed under the same license.
