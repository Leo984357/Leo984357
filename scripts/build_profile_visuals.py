"""Build the self-contained SVG presentation system for the GitHub profile."""
from pathlib import Path
from html import escape
import base64
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
BG, PANEL, LINE, INK, MUTED, ACCENT = '#111211', '#191b19', '#343834', '#e7e8e2', '#a4aaa2', '#b7c3ad'
MONO = "Menlo,Consolas,'Liberation Mono','PingFang SC','Microsoft YaHei',monospace"

def text(x,y,s,size=24,color=INK,weight=400,font=MONO,extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" font-weight="{weight}" {extra}>{escape(s)}</text>'
def rect(x,y,w,h,fill=PANEL,rx=0,stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'
def line(x1,y1,x2,y2,color=LINE,extra=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" {extra}/>'
def pixel(x,y,size=6,fill=ACCENT):
    return rect(x-size/2,y-size/2,size,size,fill)
def save(name,w,h,content,title):
    (ASSETS/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n'+rect(0,0,w,h,BG)+content+'</svg>\n')
def label(x,y,s,color=ACCENT,size=15): return text(x,y,s,size,color,500,MONO, 'letter-spacing="1.7"')
def flat_tag(x,y,s,color=ACCENT,w=None):
    width=w or len(s)*10+28
    return rect(x,y,width,32,BG,2,LINE)+text(x+14,y+22,s,14,color,500,MONO)

ascii_svg=(ASSETS/'starry-night-ascii.svg').read_text()
art=re.sub(r'^.*?<rect', '<rect', ascii_svg, count=1, flags=re.S).rsplit('</svg>',1)[0]
# Artwork itself remains a literal grid of colored ASCII glyphs.
for mobile in (False,True):
    w,h=(600,630) if mobile else (1200,696)
    scale=w/1600
    b=rect(0,0,w,43,PANEL)
    b+=pixel(23,22,7,MUTED)+pixel(39,22,7,LINE)+pixel(55,22,7,LINE)
    b+=label(78,27,'shuoren / research',MUTED,13)
    b+=f'<g transform="translate(0 44) scale({scale})">{art}</g>'
    if mobile:
        b+=label(28,292,'QUANT / DATA / CODE',ACCENT,16)
        b+=text(23,365,'SHUOREN',67,INK,600)
        b+=text(23,432,'LI.',78,INK,600)
        b+=text(183,422,'李硕仁',29,ACCENT,500)
        b+=text(28,478,'把金融问题，写成研究与工具。',25,INK,500)
        b+=text(28,518,'金融工程 @ 广东外语外贸大学',20,MUTED)
        b+=line(28,550,572,550)
        b+=label(28,586,'ALTERNATIVE DATA / ASSET PRICING',MUTED,13)
    else:
        # Keep the complete ASCII grid above a separate, flat text area.
        b+=label(36,504,'QUANTITATIVE RESEARCH × DATA ENGINEERING',ACCENT,16)
        b+=text(30,604,'SHUOREN LI.',92,INK,600)
        b+=text(820,554,'李硕仁',32,ACCENT,500)
        b+=text(820,592,'金融工程 @ GDUFS',21,MUTED)
        b+=line(36,630,1164,630)
        b+=text(36,671,'把金融问题，写成研究与工具。',24,INK)
        b+=label(772,669,'ALTERNATIVE DATA / ASSET PRICING',MUTED,12)
    save('profile-hero'+('-mobile' if mobile else '')+'.svg',w,h,b,'Shuoren Li 李硕仁 · Quant research and data engineering · The Starry Night in colored ASCII')

for name,title,subtitle,color in [('nav-portfolio.svg','ENTER THE LAB','互动作品集',ACCENT),('nav-email.svg','SAY HELLO','联系我',ACCENT),('nav-source.svg','EXPLORE CODE','浏览项目',ACCENT)]:
    b=rect(1,1,394,76,PANEL,2,LINE)+text(22,32,title,19,INK,700,MONO)+text(22,58,subtitle,15,MUTED)+text(353,46,'↗',29,color)
    save(name,396,78,b,title+' · '+subtitle)

for name,english,chinese,color in [('nav-portfolio-mobile.svg','LAB ↗','作品集',ACCENT),('nav-email-mobile.svg','EMAIL ↗','联系我',ACCENT),('nav-source-mobile.svg','CODE ↗','项目',ACCENT)]:
    b=rect(1,1,138,84,PANEL,2,LINE)+text(13,31,english,17,color,500,MONO)+text(13,65,chinese,23,INK,600)
    save(name,140,86,b,chinese)

for name,tag,title,color in [('section-work-mobile.svg','01—03 / SELECTED WORK','研究，从这里开始。',ACCENT),('section-index-mobile.svg','RESEARCH INDEX','更多实验，更多路径。',ACCENT)]:
    b=label(2,28,tag,color,17)+text(0,83,title,38,INK,600)
    save(name,600,110,b,title)

b=label(2,27,'01—03 / SELECTED WORK',ACCENT,14)+text(0,79,'研究，从这里开始。',40,INK,600)+line(432,66,1198,66)
save('section-work.svg',1200,105,b,'精选项目 Selected work')
b=label(2,27,'RESEARCH INDEX',ACCENT,14)+text(0,74,'更多实验，更多路径。',35,INK,500)+line(438,63,1198,63)
save('section-index.svg',1200,100,b,'更多研究与工具')

preview=base64.b64encode((ASSETS/'workbench-preview.png').read_bytes()).decode()
for mobile in (False,True):
    w,h=(600,870) if mobile else (1200,404)
    b=rect(1,1,w-2,h-2,PANEL,2,LINE)+rect(1,30,3,78,ACCENT)
    b+=label(30,42,'01 / FINANCIAL DATA ENGINEERING',ACCENT,14)
    b+=text(30,102,'委托理财分析框架',37 if mobile else 36,INK,600)
    b+=text(30,146,'从公开公告，到可追溯的研究工作台。',22,MUTED)
    b+=text(30,182,'交易抽取 · 生命周期 · 公司—机构关系',20,MUTED)
    for x,big,small in [(30,'16','样例公司'),(200,'4,372','交易记录'),(397,'314','金融机构')]:
        b+=text(x,249,big,40,INK,600,MONO)+text(x,278,small,17,MUTED)
    b+=label(30,320,'PUBLIC SAMPLE / 2026-08-25',ACCENT,13)
    b+=text(30,365,'查看真实界面与运行说明 ↗',21,ACCENT,600)
    if mobile: px,py,pw,ph=28,398,544,378
    else:px,py,pw,ph=650,28,520,361
    b+=rect(px-1,py-1,pw+2,ph+2,BG,2,LINE)
    b+=f'<image x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMin meet" xlink:href="data:image/png;base64,{preview}"/>'
    if mobile:b+=label(28,823,'SOURCE → RECORDS → RELATIONSHIPS',MUTED,14)
    save('project-wealth'+('-mobile' if mobile else '')+'.svg',w,h,b,'上市公司委托理财分析框架：16家公司、4372条交易、314家机构，真实脱敏样例截图。查看项目。')

for mobile in (False,True):
    w,h=(600,665) if mobile else (1200,348)
    b=rect(1,1,w-2,h-2,PANEL,2,LINE)+rect(1,29,3,75,ACCENT)
    b+=label(30,43,'02 / QUANTITATIVE RESEARCH',ACCENT,14)
    b+=text(30,100,'QMT Investment',35,INK,600)+text(30,143,'Assistant',35,INK,600)
    b+=text(30,190,'把因子想法，放进可复核的实验。',22,MUTED)
    b+=flat_tag(30,219,'LightGBM',ACCENT)+flat_tag(150,219,'Ridge',ACCENT)+flat_tag(240,219,'MOCK EXECUTION',ACCENT)
    b+=text(30,300,'方法 · 成本后回测 · 运行档案 ↗',21,ACCENT,500)
    x,y=(40,365) if mobile else (650,67)
    for xx,yy,tt,sub in [(x,y,'DATA','时间与口径'),(x+280,y,'FACTORS','候选与治理'),(x,y+160,'BACKTEST','成本与评审'),(x+280,y+160,'MODELS','训练与验证')]:
        b+=rect(xx,yy,200,84,BG,2,LINE)+label(xx+17,yy+32,tt,ACCENT,17)+text(xx+17,yy+62,sub,18,MUTED)
    b+=f'<path d="M{x+200} {y+42}H{x+280} M{x+380} {y+84}V{y+160} M{x+280} {y+202}H{x+200}" fill="none" stroke="{LINE}" stroke-width="2"/>'
    save('project-qmt'+('-mobile' if mobile else '')+'.svg',w,h,b,'QMT Investment Assistant：LightGBM、Ridge、配置化实验、成本后回测与模拟执行。')

for mobile in (False,True):
    w,h=(600,740) if mobile else (1200,348)
    b=rect(1,1,w-2,h-2,PANEL,2,LINE)+rect(1,29,3,75,ACCENT)
    b+=label(30,43,'03 / AGENT RESEARCH WORKFLOW',ACCENT,14)
    b+=text(30,108,'公募基金投研 Skill',36,INK,600)
    b+=text(30,155,'从截图、持仓与问题，到有来源的报告。',22,MUTED)
    b+=text(30,191,'材料识别 / 公开核验 / 风险计算 / 组合研究',19,MUTED)
    b+=flat_tag(30,224,'PYTHON',ACCENT)+flat_tag(131,224,'AGENT SKILL',ACCENT)
    b+=text(30,306,'安装、示例与完整诊断报告 ↗',21,ACCENT,500)
    x,y=(32,362) if mobile else (650,32)
    b+=rect(x,y,518,284,BG,2,LINE)+label(x+22,y+32,'RESEARCH CASE / 001',ACCENT,15)
    b+=line(x+22,y+49,x+496,y+49)
    for idx,(label_,tail) in enumerate([('01  INPUT','基金代码 / 截图 / 持仓'),('02  VERIFY','来源 / 截止日 / 比较窗口'),('03  COMPUTE','收益 / 回撤 / 组合暴露'),('04  REPORT','结论 / 证据 / 复核条件')]):
        yy=y+86+idx*50
        b+=pixel(x+25,yy-6,6,ACCENT)+text(x+41,yy,label_,15,INK,500,MONO)+text(x+205,yy,tail,17,MUTED)
    if mobile:b+=text(32,695,'含可复现的合成净值案例',19,ACCENT)
    save('project-fund'+('-mobile' if mobile else '')+'.svg',w,h,b,'公募基金投研 Skill：基金材料识别、公开数据核验、计算与研究报告。')

# Small linked panels remain distinct clickable repository targets.
mini=[('event','CAPITAL EVENTS','资本事件引擎','公告关联 / 状态迁移 / 证据链',ACCENT),('hidden','FACTOR DIAGNOSTICS','Hidden Pairs Factor','持仓关系 / 时间切分 / 负结果',ACCENT),('pool','FUND RESEARCH','Fund Pool Model','净值入库 / 评分 / 权重与日报',ACCENT),('audit','AUDIT PROTOTYPE','Strategy Audit','Solidity / Hardhat / 研究存证',ACCENT),('remote','REMOTE WORKFLOW','多机协作工作流','任务路由 / 远程计算 / 恢复备份',ACCENT),('about','RESEARCH & BACKGROUND','研究与经历','另类数据 / AI 暴露 / 资产定价',ACCENT)]
for slug,tag,title,desc,color in mini:
    b=rect(1,1,1198,118,PANEL,2,LINE)+text(28,71,title,30,INK,600)+label(535,44,tag,color,13)+text(535,81,desc,21,MUTED)+text(1140,78,'↗',33,color)
    save('index-'+slug+'.svg',1200,120,b,title+'：'+desc)
    b=rect(1,1,598,176,PANEL,2,LINE)+label(25,35,tag,color,13)+text(25,86,title,32,INK,600)+text(25,133,desc,21,MUTED)+text(546,93,'↗',28,color)
    save('index-'+slug+'-mobile.svg',600,178,b,title+'：'+desc)

for mobile in (False,True):
    w,h=(600,310) if mobile else (1200,210)
    b=rect(0,0,w,h,PANEL,2)+label(28,38,'TOOLS OF THE TRADE',ACCENT,14)
    b+=text(28,93,'Python  /  SQL  /  LightGBM',27 if mobile else 31,INK,500,MONO)
    if mobile:
        b+=text(28,139,'pandas  /  scikit-learn',25,MUTED,400,MONO)+text(28,182,'SQLite  /  Git  /  LaTeX',25,MUTED,400,MONO)+text(28,262,'金融工程 @ GDUFS · 2023—2027',21,ACCENT)
    else:
        b+=text(28,142,'pandas  /  scikit-learn  /  SQLite  /  Git  /  LaTeX',21,MUTED,400,MONO)+text(805,72,'GDUFS',34,ACCENT,600)+text(805,113,'金融工程 · 2023—2027',20,MUTED)+text(805,157,'研究问题 → 可复核的实现',20,MUTED)
    save('profile-tools'+('-mobile' if mobile else '')+'.svg',w,h,b,'常用工具：Python、SQL、LightGBM、pandas、scikit-learn、SQLite、Git、LaTeX。广东外语外贸大学金融工程在读。')
print('Built GitHub profile SVG assets')
