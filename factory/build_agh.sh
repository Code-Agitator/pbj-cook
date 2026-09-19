#!/usr/bin/env bash
# 将 Shadowrocket 模块规则转换为 AdGuard Home DNS 过滤语法并生成 *_agh.txt
# 规则映射: DOMAIN/DOMAIN-SUFFIX -> ||domain^ ; DOMAIN-KEYWORD -> 裸关键字(子串匹配)
# IP-CIDR 无法在 DNS 层拦截, 跳过
set -euo pipefail
cd "$(dirname "$0")/.."

to_agh() {
  awk -F, '
    /^#!/ { next }
    /^#/ { line=$0; sub(/^#/, "!", line); print line; next }
    /^DOMAIN-KEYWORD,/ { print $2; next }
    /^DOMAIN,/ { print "||" $2 "^"; next }
    /^DOMAIN-SUFFIX,/ { print "||" $2 "^"; next }
  ' "$1"
}

{
  echo '! 本文件由 factory/build_agh.sh 自动生成, 请勿手动编辑'
  echo '! 来源: custom_reject_list.module (Cowjiang/shadowrocket-rules)'
  to_agh custom_reject_list.module
} > agh_custom_reject.txt

{
  echo '! 本文件由 factory/build_agh.sh 自动生成, 请勿手动编辑'
  echo '! 来源: sr_reject_list.module (Cowjiang/shadowrocket-rules)'
  to_agh sr_reject_list.module
} > agh_sr_reject.txt

echo "agh_custom_reject.txt: $(grep -c '^[^!]' agh_custom_reject.txt) 条规则"
echo "agh_sr_reject.txt: $(grep -c '^[^!]' agh_sr_reject.txt) 条规则"

# 生成 iOS DoT 描述文件(端口/协议变更时 CI 会自动更新此文件)
# UUID 使用固定值, 保证配置不变时文件内容稳定
UUID1="7A3F2C91-5E84-4D6B-9A12-C3D8F0E51B47"
UUID2="B8D6E204-91A7-4F35-8C29-D1E6A7B30F58"
cat > Cowjiang-AdGuard.mobileconfig <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>PayloadContent</key>
	<array>
		<dict>
			<key>DNSSettings</key>
			<dict>
				<key>DNSProtocol</key>
				<string>TLS</string>
				<key>ServerName</key>
				<string>dns.inceptae.com</string>
			</dict>
			<key>PayloadDescription</key>
			<string>https://github.com/Cowjiang</string>
			<key>PayloadDisplayName</key>
			<string>Cowjiang AdGuard</string>
			<key>PayloadIdentifier</key>
			<string>com.apple.dnsSettings.managed.dns.inceptae.dot</string>
			<key>PayloadOrganization</key>
			<string>Cowjiang</string>
			<key>PayloadType</key>
			<string>com.apple.dnsSettings.managed</string>
			<key>PayloadUUID</key>
			<string>$UUID1</string>
			<key>PayloadVersion</key>
			<integer>1</integer>
			<key>ProhibitDisablement</key>
			<false/>
		</dict>
	</array>
	<key>PayloadDescription</key>
	<string>Cowjiang AdGuard — 加密 DNS (DoT) 广告过滤，规则每日自动更新</string>
	<key>PayloadDisplayName</key>
	<string>Cowjiang AdGuard</string>
	<key>PayloadIdentifier</key>
	<string>inceptae.dot.profile</string>
	<key>PayloadOrganization</key>
	<string>Cowjiang</string>
	<key>PayloadRemovalDisallowed</key>
	<false/>
	<key>PayloadType</key>
	<string>Configuration</string>
	<key>PayloadUUID</key>
	<string>$UUID2</string>
	<key>PayloadVersion</key>
	<integer>1</integer>
</dict>
</plist>
EOF
echo "Cowjiang-AdGuard.mobileconfig: 已生成"
