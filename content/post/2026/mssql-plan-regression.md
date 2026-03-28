---
title: "MSSQL执行计划突变问题"
description: "最近遇到了一个MSSQL执行计划突变问题（plan regression），本文记录一下背景和排查过程，以及解决方案。"
date: 2026-03-28T21:10:00+11:00
categories:
  - 学习
tags:
  - 数据库
---

## 背景

最近在编写SQL的时候，遇到一个神奇的问题。我们的测试环境数据库是每周从正式环境复制一份。我在测试环境上运行我编写好的SQL时，一切正常，但是当部署到正式环境后，这个SQL变得特别特别慢。原来可能需要200ms的，在正式环境需要20s。

## 排查过程

因为我写的SQL是很复杂的一大串（其实是 Store Procedure），所以首先是定位具体是哪个SQL拖慢了速度。通过二分调试法，最后定位到了这个语句：

```sql
WITH Top6BaseDateTimeUTC AS (
    SELECT TOP 6 BaseDateTimeUTC
    FROM (
        SELECT BaseDateTimeUTC
        FROM GWForecasts WITH (NOLOCK)
        WHERE Product = 'WTHRBIT1HR'
        GROUP BY BaseDateTimeUTC
    ) t
    ORDER BY BaseDateTimeUTC DESC
)
SELECT DISTINCT
    f.Lat,
    f.Lon
INTO #ForecastGridWB
FROM GWForecasts f WITH (NOLOCK)
JOIN Top6BaseDateTimeUTC t
    ON f.BaseDateTimeUTC = t.BaseDateTimeUTC
WHERE f.Product = 'WTHRBIT1HR';
```

这里从`GWForecasts`中捞数据，而这个表有几千万行数据。我试了一下在正式环境将`TOP 6`改成`TOP 5`，速度瞬间快了起来。而在测试环境，`TOP 6`速度是很快的。因此我怀疑这里可能有个阈值，超过了它，就会导致性能突变。

于是我尝试在测试环境把`TOP 6`改大，最后在`TOP 11`的时候，出现了性能突变问题。所以我现在可以在测试环境复现问题了，虽然阈值不一样。

因为测试环境的数据库是每周同步一次数据，所以测试环境的数据数量是比正式环境要少的。因此这个阈值不一样，也算合理。

经过一番询问AI，它告知我这个情况非常经典，叫做执行计划突变（plan regression）。当SQL Server的查询优化器在生成执行计划时，可能会选择不同的执行计划来执行查询。当查询的某些参数或数据分布发生变化时，优化器可能会选择一个不同的执行计划，这个新的执行计划可能效率更低，从而导致性能突变。

后面通过分析这个语句的执行计划，证实了这点。因为执行计划是XML格式，非常长，且不适合人看，所以我就不放上来了。

我用Gemini写了一个执行计划可视化网页，大家也可以试试看：[SQL Server Query Plan Visualiser](https://chn-lee-yumi.github.io/SQL-Server-Query-Plan-Visualiser/)

## 解决方案

通过使用一个临时表解决了这个问题：（解决方案也是AI给的）

```sql
SELECT DISTINCT TOP 6 BaseDateTimeUTC
INTO #TopBaseDateTimeUTC
FROM GWForecasts WITH (NOLOCK)
WHERE Product = 'WTHRBIT1HR'
ORDER BY BaseDateTimeUTC DESC;

SELECT DISTINCT
    f.Lat,
    f.Lon
INTO #ForecastGridWB
FROM GWForecasts f WITH (NOLOCK)
JOIN #TopBaseDateTimeUTC t
    ON f.BaseDateTimeUTC = t.BaseDateTimeUTC
WHERE f.Product = 'WTHRBIT1HR';
```
