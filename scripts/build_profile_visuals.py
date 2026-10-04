"""Build the self-contained SVG presentation system for the GitHub profile."""
from pathlib import Path
from html import escape
import base64
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
BG, PANEL, LINE, INK, MUTED, CYAN, GOLD = '#080d14', '#101a27', '#263548', '#eaf0f7', '#9aabc0', '#5fe1ec', '#f4c866'
SANS = "Arial,'PingFang SC','Microsoft YaHei',sans-serif"
MONO = "Menlo,Consolas,monospace"

def text(x,y,s,size=24,color=INK,weight=400,font=SANS,extra=''):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" font-weight="{weight}" {extra}>{escape(s)}</text>'
def rect(x,y,w,h,fill=PANEL,rx=0,stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}"/>'
def line(x1,y1,x2,y2,color=LINE,extra=''):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" {extra}/>'
def circle(x,y,r,fill=CYAN,extra=''):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" {extra}/>'
def save(name,w,h,content,title):
    (ASSETS/name).write_text(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">\n<title>{escape(title)}</title>\n'+rect(0,0,w,h,BG)+content+'</svg>\n')
def label(x,y,s,color=CYAN,size=15): return text(x,y,s,size,color,500,MONO, 'letter-spacing="1.7"')
def pill(x,y,s,color=CYAN,w=None):
    width=w or len(s)*10+28
    return rect(x,y,width,32,'#142332',16)+text(x+14,y+22,s,14,color,500,MONO)

ascii_svg=(ASSETS/'starry-night-ascii.svg').read_text()
art=re.sub(r'^.*?<rect', '<rect', ascii_svg, count=1, flags=re.S).rsplit('</svg>',1)[0]
# Artwork itself remains a literal grid of colored ASCII glyphs.
for mobile in (False,True):
    w,h=(600,630) if mobile else (1200,590)
    scale=w/1600
    b='<defs><linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#080d14" stop-opacity="0"/><stop offset="1" stop-color="#080d14"/></linearGradient></defs>'
    b+=rect(0,0,w,43,'#0e1621')
    b+=circle(23,22,4,GOLD)+circle(39,22,4,CYAN)+circle(55,22,4,'#63758c')
    b+=label(78,27,'shuoren / research',MUTED,13)
    b+=f'<g transform="translate(0 44) scale({scale})">{art}</g>'
    if mobile:
        b+=rect(0,194,600,75,'url(#fade)')
        b+=label(28,292,'QUANT / DATA / CODE',CYAN,16)
        b+=text(23,365,'SHUOREN',67,INK,800,extra='letter-spacing="-3"')
        b+=text(23,432,'LI.',78,INK,800,extra='letter-spacing="-3"')
        b+=text(183,422,'李硕仁',29,GOLD,500)
        b+=text(28,478,'把金融问题，写成研究与工具。',25,INK,500)
        b+=text(28,518,'金融工程 @ 广东外语外贸大学',20,MUTED)
        b+=line(28,550,572,550)
        b+=label(28,586,'ALTERNATIVE DATA / ASSET PRICING',MUTED,13)
    else:
        b+=rect(0,300,1200,165,'url(#fade)')
        b+=label(36,398,'QUANTITATIVE RESEARCH × DATA ENGINEERING',CYAN,16)
        b+=text(30,498,'SHUOREN LI.',96,INK,800,extra='letter-spacing="-5"')
        b+=text(820,448,'李硕仁',32,GOLD,500)
        b+=text(820,486,'金融工程 @ GDUFS',21,MUTED)
        b+=line(36,524,1164,524)
        b+=text(36,565,'把金融问题，写成研究与工具。',24,INK)
        b+=label(772,563,'ALTERNATIVE DATA / ASSET PRICING',MUTED,12)
    b+='<style>@keyframes travel{0%{stroke-dashoffset:300}100%{stroke-dashoffset:0}}.beam{stroke-dasharray:80 220;animation:travel 8s linear infinite}@media(prefers-reduced-motion:reduce){.beam{animation:none}}</style>'
    b+=line(1,h-2,w-1,h-2,CYAN,'stroke-width="2" class="beam"')
    save('profile-hero'+('-mobile' if mobile else '')+'.svg',w,h,b,'Shuoren Li 李硕仁 · Quant research and data engineering · The Starry Night in colored ASCII')

for name,title,subtitle,color in [('nav-portfolio.svg','ENTER THE LAB','互动作品集',CYAN),('nav-email.svg','SAY HELLO','联系我',GOLD),('nav-source.svg','EXPLORE CODE','浏览项目',CYAN)]:
    b=rect(1,1,394,76,PANEL,8,LINE)+text(22,32,title,19,INK,700,MONO)+text(22,58,subtitle,15,MUTED)+text(353,46,'↗',29,color)
    save(name,396,78,b,title+' · '+subtitle)

for name,english,chinese,color in [('nav-portfolio-mobile.svg','LAB ↗','作品集',CYAN),('nav-email-mobile.svg','EMAIL ↗','联系我',GOLD),('nav-source-mobile.svg','CODE ↗','项目',CYAN)]:
    b=rect(1,1,138,84,PANEL,8,LINE)+text(13,31,english,17,color,500,MONO)+text(13,65,chinese,23,INK,600)
    save(name,140,86,b,chinese)

for name,tag,title,color in [('section-work-mobile.svg','01—03 / SELECTED WORK','研究，从这里开始。',CYAN),('section-index-mobile.svg','RESEARCH INDEX','更多实验，更多路径。',GOLD)]:
    b=label(2,28,tag,color,17)+text(0,83,title,38,INK,600)
    save(name,600,110,b,title)

b=label(2,27,'01—03 / SELECTED WORK',CYAN,14)+text(0,79,'研究，从这里开始。',40,INK,600)+line(432,66,1198,66)
save('section-work.svg',1200,105,b,'精选项目 Selected work')
b=label(2,27,'RESEARCH INDEX',GOLD,14)+text(0,74,'更多实验，更多路径。',35,INK,500)+line(438,63,1198,63)
save('section-index.svg',1200,100,b,'更多研究与工具')

preview=base64.b64encode((ASSETS/'workbench-preview.png').read_bytes()).decode()
for mobile in (False,True):
    w,h=(600,870) if mobile else (1200,404)
    b=rect(1,1,w-2,h-2,PANEL,14,LINE)+rect(1,30,3,78,CYAN)
    b+=label(30,42,'01 / FINANCIAL DATA ENGINEERING',CYAN,14)
    b+=text(30,102,'委托理财分析框架',37 if mobile else 36,INK,600)
    b+=text(30,146,'从公开公告，到可追溯的研究工作台。',22,MUTED)
    b+=text(30,182,'交易抽取 · 生命周期 · 公司—机构关系',20,MUTED)
    for x,big,small in [(30,'16','样例公司'),(200,'4,372','交易记录'),(397,'314','金融机构')]:
        b+=text(x,249,big,40,INK,600,MONO)+text(x,278,small,17,MUTED)
    b+=label(30,320,'PUBLIC SAMPLE / 2026-08-25',GOLD,13)
    b+=text(30,365,'查看真实界面与运行说明 ↗',21,CYAN,600)
    if mobile: px,py,pw,ph=28,398,544,378
    else:px,py,pw,ph=650,28,520,361
    b+=rect(px-1,py-1,pw+2,ph+2,'#172737',7,LINE)
    b+=f'<image x="{px}" y="{py}" width="{pw}" height="{ph}" preserveAspectRatio="xMidYMin meet" xlink:href="data:image/png;base64,{preview}"/>'
    if mobile:b+=label(28,823,'SOURCE → RECORDS → RELATIONSHIPS',MUTED,14)
    save('project-wealth'+('-mobile' if mobile else '')+'.svg',w,h,b,'上市公司委托理财分析框架：16家公司、4372条交易、314家机构，真实脱敏样例截图。查看项目。')

for mobile in (False,True):
    w,h=(600,665) if mobile else (1200,348)
    b=rect(1,1,w-2,h-2,PANEL,14,LINE)+rect(1,29,3,75,GOLD)
    b+=label(30,43,'02 / QUANTITATIVE RESEARCH',GOLD,14)
    b+=text(30,100,'QMT Investment',35,INK,600)+text(30,143,'Assistant',35,INK,600)
    b+=text(30,190,'把因子想法，放进可复核的实验。',22,MUTED)
    b+=pill(30,219,'LightGBM',GOLD)+pill(150,219,'Ridge',GOLD)+pill(240,219,'MOCK EXECUTION',GOLD)
    b+=text(30,300,'方法 · 成本后回测 · 运行档案 ↗',21,CYAN,500)
    x,y=(40,365) if mobile else (650,67)
    for xx,yy,tt,sub in [(x,y,'DATA','时间与口径'),(x+280,y,'FACTORS','候选与治理'),(x,y+160,'BACKTEST','成本与评审'),(x+280,y+160,'MODELS','训练与验证')]:
        b+=rect(xx,yy,200,84,'#0b121d',8,LINE)+label(xx+17,yy+32,tt,CYAN,17)+text(xx+17,yy+62,sub,18,MUTED)
    b+=f'<path d="M{x+200} {y+42}H{x+280} M{x+380} {y+84}V{y+160} M{x+280} {y+202}H{x+200}" fill="none" stroke="{GOLD}" stroke-width="2" stroke-dasharray="5 8" class="flow"/>'
    b+='<style>@keyframes flow{to{stroke-dashoffset:-52}}.flow{animation:flow 4s linear infinite}@media(prefers-reduced-motion:reduce){.flow{animation:none}}</style>'
    save('project-qmt'+('-mobile' if mobile else '')+'.svg',w,h,b,'QMT Investment Assistant：LightGBM、Ridge、配置化实验、成本后回测与模拟执行。')

for mobile in (False,True):
    w,h=(600,740) if mobile else (1200,348)
    b=rect(1,1,w-2,h-2,PANEL,14,LINE)+rect(1,29,3,75,CYAN)
    b+=label(30,43,'03 / AGENT RESEARCH WORKFLOW',CYAN,14)
    b+=text(30,108,'公募基金投研 Skill',36,INK,600)
    b+=text(30,155,'从截图、持仓与问题，到有来源的报告。',22,MUTED)
    b+=text(30,191,'材料识别 / 公开核验 / 风险计算 / 组合研究',19,MUTED)
    b+=pill(30,224,'PYTHON',CYAN)+pill(131,224,'AGENT SKILL',CYAN)
    b+=text(30,306,'安装、示例与完整诊断报告 ↗',21,CYAN,500)
    x,y=(32,362) if mobile else (650,32)
    b+=rect(x,y,518,284,'#0b121d',10,LINE)+label(x+22,y+32,'RESEARCH CASE / 001',GOLD,15)
    b+=line(x+22,y+49,x+496,y+49)
    for idx,(label_,tail) in enumerate([('01  INPUT','基金代码 / 截图 / 持仓'),('02  VERIFY','来源 / 截止日 / 比较窗口'),('03  COMPUTE','收益 / 回撤 / 组合暴露'),('04  REPORT','结论 / 证据 / 复核条件')]):
        yy=y+86+idx*50
        b+=circle(x+25,yy-6,3,CYAN)+text(x+41,yy,label_,15,INK,500,MONO)+text(x+205,yy,tail,17,MUTED)
    if mobile:b+=text(32,695,'含可复现的合成净值案例',19,GOLD)
    save('project-fund'+('-mobile' if mobile else '')+'.svg',w,h,b,'公募基金投研 Skill：基金材料识别、公开数据核验、计算与研究报告。')

# Small linked panels remain distinct clickable repository targets.
mini=[('event','CAPITAL EVENTS','资本事件引擎','公告关联 / 状态迁移 / 证据链',CYAN),('hidden','FACTOR DIAGNOSTICS','Hidden Pairs Factor','持仓关系 / 时间切分 / 负结果',GOLD),('pool','FUND RESEARCH','Fund Pool Model','净值入库 / 评分 / 权重与日报',CYAN),('audit','AUDIT PROTOTYPE','Strategy Audit','Solidity / Hardhat / 研究存证',GOLD),('remote','REMOTE WORKFLOW','多机协作工作流','任务路由 / 远程计算 / 恢复备份',CYAN),('about','RESEARCH & BACKGROUND','研究与经历','另类数据 / AI 暴露 / 资产定价',GOLD)]
for slug,tag,title,desc,color in mini:
    b=rect(1,1,1198,118,PANEL,10,LINE)+text(28,71,title,30,INK,600)+label(535,44,tag,color,13)+text(535,81,desc,21,MUTED)+text(1140,78,'↗',33,color)
    save('index-'+slug+'.svg',1200,120,b,title+'：'+desc)
    b=rect(1,1,598,176,PANEL,10,LINE)+label(25,35,tag,color,13)+text(25,86,title,32,INK,600)+text(25,133,desc,21,MUTED)+text(546,93,'↗',28,color)
    save('index-'+slug+'-mobile.svg',600,178,b,title+'：'+desc)

for mobile in (False,True):
    w,h=(600,310) if mobile else (1200,210)
    b=rect(0,0,w,h,'#0b1420',12)+label(28,38,'TOOLS OF THE TRADE',CYAN,14)
    b+=text(28,93,'Python  /  SQL  /  LightGBM',27 if mobile else 31,INK,500,MONO)
    if mobile:
        b+=text(28,139,'pandas  /  scikit-learn',25,MUTED,400,MONO)+text(28,182,'SQLite  /  Git  /  LaTeX',25,MUTED,400,MONO)+text(28,262,'金融工程 @ GDUFS · 2023—2027',21,GOLD)
    else:
        b+=text(28,142,'pandas  /  scikit-learn  /  SQLite  /  Git  /  LaTeX',21,MUTED,400,MONO)+text(805,72,'GDUFS',34,GOLD,600)+text(805,113,'金融工程 · 2023—2027',20,MUTED)+text(805,157,'研究问题 → 可复核的实现',20,MUTED)
    save('profile-tools'+('-mobile' if mobile else '')+'.svg',w,h,b,'常用工具：Python、SQL、LightGBM、pandas、scikit-learn、SQLite、Git、LaTeX。广东外语外贸大学金融工程在读。')
print('Built GitHub profile SVG assets')
