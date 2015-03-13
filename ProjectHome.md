# In English #

This project focus on creating an input method back-end for different kind of input method front-end in different platforms.

Currently, it supports GAE and local socket service (in localhost or LAN) as back-end, vimim and ibus as front-end.

The Chinese pinyin and shuangpin have been worked out. Wubi is under development.

We're looking forward to add more front-end and back-end engines.


---

# 中文 #

这个项目的目标是创建个人私有的运行于局域网或本机的云输入法。它可能应用于这些情形：
  * 你需要云输入法带来的便利，但是又担心远程的云缺乏私密性和定制性
  * 你访问远程云需要的 Internet 连接速度很慢
  * 你处在根本无法访问远程服务器的局域网中

除了上面几个缺点之外，云输入法的好处是显而易见的：
  1. 由于所有词库均在远端，因此词库并不占用本机内存。
  1. 由于所有算法均在远端，因此不耗费本机CPU。
  1. 多台机器共享词库。

本项目提供了一个例子，它创建了一个基本的云后端，并且利用 ibus 书写了一个非常简单的前端。这个ibus前端非常之简单，以致于足够可以作为撰写 ibus 输入法引擎的例子。

提供了GAE云作为例子，但是它存在的价值不大，因为如果你能快速访问GAE，直接使用网上的云输入服务更合适，这里的主要目标仍然是保存在本机或者局域网的云输入。