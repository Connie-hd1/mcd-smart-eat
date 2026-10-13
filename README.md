# 麦省钱 · 今天吃啥 (mcd-smart-eat)

> 一个懂你预算的麦当劳点餐助手。不用算券，不用纠结，直接告诉你今天吃什么最划算。

## 😫 解决什么痛点？
每次想吃麦当劳，都要面对两个灵魂拷问：
1. **预算有限**：我只想花 20 块，怎么点才不会超支？
2. **选择困难**：菜单太多、优惠券太复杂，到底吃什么最划算？

**麦省钱** 就是为了解决这两个问题，让点餐回归简单。

## ✨ 核心功能
- 🎯 **预算硬约束**：输入你的预算（比如 15元/20元），直接淘汰超支选项。
- 🍔 **智能组合推荐**：结合麦当劳 MCP 的菜单、优惠券、门店数据，给出性价比最高的 1-3 个组合。
- 💰 **省了多少一目了然**：对比原价和到手价，告诉你这顿省了多少钱。
- 🍟 **口味与场景匹配**：不辣、想吃肉、想吃鸡块、还是只想随便吃点，它都能听懂。

## 🚀 如何使用
[capture_20261013201126346.bmp](https://github.com/user-attachments/files/33385993/capture_20261013201126346.bmp)
[capture_20261013201149621.bmp](https://github.com/user-attachments/files/33386040/capture_20261013201149621.bmp)
[capture_20261013201211819.bmp](https://github.com/user-attachments/files/33386046/capture_20261013201211819.bmp)
[capture_20261013201608262.bmp](https://github.com/user-attachments/files/33386053/capture_20261013201608262.bmp)
[capture_20261013201628691.bmp](https://github.com/user-attachments/files/33386057/capture_20261013201628691.bmp)
[capture_20261013201853988.bmp](https://github.com/user-attachments/files/33386061/capture_20261013201853988.bmp)

1. 配置麦当劳 MCP Token
2. 输入预算和口味需求
3. 得到最佳点餐方案

## 🛠️ 技术实现
- **开发工具**：WorkBuddy
- **数据连接**：麦当劳 MCP（使用了菜单、优惠券、门店等工具）
- **底层逻辑**：基于预算约束与评分规则进行组合推荐

## 📂 项目文件说明
- `README.md`：项目介绍
- `CONTEST_DECLARATION.md`：参赛声明
- `MCP_INTEGRATION.md`：MCP 工具调用说明
- `workbuddy.md`：WorkBuddy 开发对话上下文（用于比赛积分）

---
*本项目参与麦当劳中国程序员创意开发大赛*
