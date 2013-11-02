ServerClusterManageTool
=======================

ServerClusterManageTool is a tool to help 


##背景
随着云计算服务的普及，基于云计算的PaaS、IaaS受到越来越多的关注，使用这些服务的用户也越来越多。对于一些大型的应用而言，可能包含多种服务，而这些服务需要部署在多台服务器上。例如：某个应用可能部署了10台数据库服务器，10台Web Http服务器以及5台静态文件存储服务器等。那么作为应用程序管理员来说，一台一台地登录去管理这些机器显得非常繁琐，而且对于同一种服务（比如数据库服务）的机器需要执行的管理任务又都大致相同，那么对每台机器进行重复的工作也会增加集群管理员的负担。

 应对上述需求场景，我开发了这样一个基于脚本的服务器集群管理工具，它主要具有如下功能和优点：
 
* 针对不同应用场景，对服务器进行高效的分组管理。

* 以可执行脚本作为子任务，可以自定义脚本内容，具有高度灵活性。以多个脚本组成的有序组序列作为可执行任务单元。脚本可分组，同组内可排序，有效组织和管理。

* 针对不同需求，创建<code>服务器组<->脚本组</code>的执行任务。随时启动该任务，便可下达对该服务器组的基于脚本序列的任务执行命令。

* 提供对<code>服务器组<->脚本组</code>的执行任务的运行状态查询，便于监控。可以查看远程服务器控制台的输出显示，当前运行状态，执行到哪个脚本，哪个脚本有异常等等信息。

##应用场景举例
假如我想为我的10台机器同时安装LAMP。那么首先我们建立一个服务器组<code>server_group</code>，并将这10台机器加入到该组中。接下来，我们创建三个脚本，分别为<code>Setup_Apache</code>，<code>Setup_Mysql</code>，<code>Setup_PHP</code>，然后我们再创建一个脚本组，命名为LAMP_Group，并将前面的三个脚本添加到该组来，并在组内排好顺序（针对有执行顺序要求的任务）。最后，我们创建一个可执行任务<code><server_group , LAMP_Group></code>并执行，再状态查询页面中监控该任务的在不同服务器上的个脚本执行情况。

过一段时间，我又想为另一个服务器组安装某些服务，也需要使用到<code>Mysql</code> ，那么就可以将之前创建的<code>Setup_Mysql</code>脚本复用添加，再增加一些其他需要的脚本，生成新的脚本组。

或是，我突然想查看集群上的某个日志文件，那么编写一个将日志文件内容打印到控制台的脚本，对该集群执行该脚本，再通过监控页面得到远程主机的控制台输出结果，方便查看。

##技术实现
* 系统环境：<code>linux（ubuntu）</code>
* 使用到技术及模块：python2.6 ，pexpect ，web.py（轻量级web框架） ， sqlalchemy（ORM） ， mysql ，  jQuery ， Twitter Bootstrap。
* 项目包括控制台console和web两个应用
* Console 通过根据配置文件作为参数执行命令，web则更好的可以进行服务器、脚本、任务的可视化系统管理。
* Console执行：<code>./run_task.py tasks.xml</code>
* Web启动：<code>./start.sh</code>  通过浏览器访问，默认端口8080（该文件夹下的database.conf为mysql数据库的配置）
* 被管理的server需为<code>unix（linux）</code>系统，且装有<code>ssh server</code>（即可以ssh远程登录）。
* 脚本头部请填写类似<code>“#!/usr/bin/python”</code>等说明，以确保其可以正常执行。


### You can find more on my website : http://lixinzhang.github.io/Projects
