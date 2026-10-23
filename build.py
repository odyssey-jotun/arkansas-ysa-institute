#!/usr/bin/env python3
"""Builds index.html, little-rock.html and faq.html from the data below. Run: python3 build.py

Edit the class time, the address and unit meeting times here, then rebuild.
Unit times come from each unit's page on local.churchofjesuschrist.org (checked 2026-10-23).
A photo of the house goes in images/house-800.webp and images/house-858.webp; the
Little Rock page shows it automatically when those files exist.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SITE = "https://odyssey-jotun.github.io/arkansas-ysa-institute/"
NAME = "Arkansas YSA Institute"

# Where and when the Little Rock Stake class meets.
ADDRESS = {"street": "2710 Millbrook Drive", "city": "Benton", "state": "AR", "zip": "72015"}
CLASS_TIME = "Tuesdays at 7:00 PM"
CLASS_TIME_PHRASE = "on Tuesdays at 7:00 PM"
ADDR_SHORT = f"{ADDRESS['street']}, {ADDRESS['city']}"
ADDR_LINE = f"{ADDRESS['street']}, {ADDRESS['city']}, {ADDRESS['state']} {ADDRESS['zip']}"
HOUSE_PHOTO = (ROOT / "images" / "house-800.webp").exists()

STAKES = [
    {
        "id": "little-rock-stake",
        "name": "Little Rock Stake",
        "sub": "Little Rock, Benton, Hot Springs and south Arkansas",
        "class_title": "Little Rock Stake institute",
        "facts": [("clock", CLASS_TIME), ("pin", ADDR_LINE)],
        "class_note": "The class meets in a home in Benton and is open to young single and married adults ages 18 to 35, and to their friends.",
        "page": "little-rock.html",
        "units": [
            ("Little Rock Ward", "11:30 AM", "13901 Quail Run Drive, Little Rock"),
            ("Benton Ward", "9:00 AM", "13901 Quail Run Drive, Little Rock"),
            ("Pinnacle Mountain Ward", "10:00 AM", "600 South Rodney Parham Road, Little Rock"),
            ("Hot Springs Ward", "10:00 AM", "2765 Malvern Avenue, Hot Springs"),
            ("Pine Bluff Ward", "10:00 AM", "2501 Ridgway Road, Pine Bluff"),
            ("Arkadelphia Branch", "10:00 AM", "2601 Twin Rivers Drive, Arkadelphia"),
            ("Camden Branch", "10:00 AM", "859 Lakewood Road, Camden"),
            ("Glenwood Branch", "10:00 AM", "1466 Highway 70 West, Glenwood"),
            ("Hope Branch", "10:00 AM", "3069 Highway 29 North, Hope"),
            ("Malvern Branch", "1:00 PM", "519 Fairview Street, Malvern"),
            ("Monticello Branch", "9:30 AM", "519 Glenwood Drive, Monticello"),
        ],
    },
    {
        "id": "north-little-rock-stake",
        "name": "North Little Rock Stake",
        "sub": "North Little Rock, Conway and the River Valley",
        "class_title": "North Little Rock Stake institute",
        "facts": [
            ("clock", "Class night posting soon"),
            ("pin", "North Little Rock Arkansas Stake Center, 905 Kierre Drive, North Little Rock"),
        ],
        "class_note": (
            f"Until the schedule posts, young adults from either stake are welcome at the Little Rock Stake "
            f"class {CLASS_TIME_PHRASE} at {ADDR_SHORT}."
        ),
        "page": None,
        "units": [
            ("North Little Rock Ward", "10:00 AM", "905 Kierre Drive, North Little Rock"),
            ("Conway 1st Ward", "11:30 AM", "2045 Dave Ward Drive, Conway"),
            ("Conway 2nd Ward", "9:00 AM", "2045 Dave Ward Drive, Conway"),
            ("Greenbrier Ward", "9:00 AM", "6556 Heber Springs Road West, Quitman"),
            ("Morrilton Ward", "10:00 AM", "1101 Burrow Street, Morrilton"),
            ("Russellville Ward", "10:00 AM", "200 South Cumberland Avenue, Russellville"),
            ("Danville Branch", "10:00 AM", "13842 North State Highway 27, Danville"),
        ],
    },
]
UNIT_COUNT = sum(len(s["units"]) for s in STAKES)
LR_UNITS = STAKES[0]["units"]

ICONS = {
    "book": '<path d="M3 5.5C5.5 4.5 8.5 4.5 12 6.5c3.5-2 6.5-2 9-1V19c-2.5-1-5.5-1-9 1-3.5-2-6.5-2-9-1z"/><path d="M12 6.5V20"/>',
    "pin": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "person": '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c1.2-3.5 4-5 7-5s5.8 1.5 7 5"/>',
    "heart": '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/>',
    "map": '<path d="M9 4 3.5 6v14L9 18l6 2 5.5-2V4L15 6z"/><path d="M9 4v14M15 6v14"/>',
    "pencil": '<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="m13.5 6.5 4 4"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    "people": '<circle cx="9" cy="8" r="3"/><path d="M3.5 19c.8-3 3-4.5 5.5-4.5s4.7 1.5 5.5 4.5"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.6c2.2 0 3.9 1.2 4.5 3.9"/>',
    "question": '<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.5a2.5 2.5 0 1 1 3.4 2.3c-.6.3-1 .8-1 1.5v.7"/><circle cx="12" cy="16.8" r=".7" fill="currentColor" stroke="none"/>',
    "home": '<path d="M4 11.5 12 5l8 6.5"/><path d="M6 10v9.5h12V10"/><path d="M10 19.5v-5h4v5"/>',
}


def icon(name, size=26):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def esc(s):
    return html.escape(s, quote=True)


# FAQ: (question, answer HTML). Keyword notes: volumes are Ahrefs US monthly searches, 2026-10-23.
FAQ_WHEN = (
    "When and where does the Little Rock Stake institute class meet?",
    f"<p>{CLASS_TIME} at {ADDR_LINE}, a home in Benton. The North Little Rock Stake schedule will appear on its "
    "stake tab when it is set.</p>",
)
FAQ_INSTITUTE = [
    ("What is institute?",  # institute lds 1,100; lds institute 700; what is institute lds 30
     "<p>Institute of Religion is the weekly religion class that The Church of Jesus Christ of Latter-day Saints "
     "offers young adults. Classes study the scriptures and the teachings of living prophets, and they meet in "
     "meetinghouses, campus buildings and homes. Many people search for it as LDS institute or myInstitute.</p>"),
    FAQ_WHEN,
    ("Who can attend institute?",  # lds institute classes for adults 50
     "<p>Anyone ages 18 to 35. Young single adults are the heart of the class, and married young adults are welcome. "
     "Where enough students sign up, classes split into ages 18 to 25 and 26 to 35. Adults over 35 can ask their "
     "ward or stake about other classes.</p>"),
    ("Is institute free?",
     "<p>Yes. Institute courses have no cost.</p>"),
    ("Do I have to be a member of the Church to attend?",
     "<p>No. Friends of other faiths are welcome. The myInstitute Quick Signup was built for them: it asks for a name, "
     "an email and a birthdate, with no Church account required, and the institute administrator approves the request.</p>"),
    ("How do I register on myInstitute?",  # my institute lds 250
     "<ol><li>Go to myinstitute.churchofjesuschrist.org.</li>"
     "<li>Choose Find an Institute and search for Little Rock or North Little Rock, or choose Find Classes Near Me.</li>"
     "<li>On the program page, choose Find a Class.</li>"
     "<li>Pick the class and choose Register.</li>"
     "<li>Members choose Login &amp; Register with a Church account. Friends choose Quick Signup.</li></ol>"
     "<p>Once you are registered, the class appears on your myInstitute dashboard.</p>"),
    ("Can I come without registering?",
     "<p>Yes. Visit a class first and register afterward. Registering near the start of a semester gives you the "
     "best chance of earning credit.</p>"),
    ("Can I take institute online?",  # online institute lds 30; online institute classes lds 30
     "<p>Search myInstitute for online classes, which help when a work shift or a long drive keeps you from "
     "Tuesday night in Benton.</p>"),
    ("How do I earn institute credit?",
     "<ul><li>Attend at least 75 percent of class meetings.</li>"
     "<li>Finish the assigned reading: all of it for scripture courses, 75 percent for other courses.</li>"
     "<li>Complete the course's learning experiences.</li></ul>"
     "<p>Credit counts toward institute graduation. Many institute courses also transfer as religion credit to Church "
     "schools such as BYU, BYU-Idaho, BYU-Hawaii and Ensign College, and each school sets its own transfer rules.</p>"),
    ("What is a YSA ward, and what ages count as young single adults?",  # ysa ward 200; lds ysa age range 60; what is a ysa ward 50
     "<p>Since July 2024, the Church counts unmarried members ages 18 to 35 as young single adults. Single adults 36 "
     "and older belong to the single adult program. A YSA ward or branch is a congregation for young single adults, "
     "organized where enough of them live. Your bishop or branch president can tell you which unit your address "
     "belongs to, and institute is open to you either way.</p>"),
    ("Which ward or branch do I attend?",  # lds ysa ward near me 150; ysa ward near me 150
     f"<p>Your home address decides it. The <a href=\"index.html#stakes\">stake tabs on the home page</a> list all "
     f"{UNIT_COUNT} wards and branches in the two stakes. The meetinghouse locator on "
     "the Church's website shows exact boundaries.</p>"),
]

FAQ_CHURCH = [
    ("Is LDS the same as Mormon? What should I call the Church?",  # is lds mormon 1,700; what does lds stand for 1,100; what is lds 2,700
     "<p>Both are older nicknames for the same church. LDS is short for Latter-day Saints. In 2018, President Russell "
     "M. Nelson asked that the Church be called by its full name, The Church of Jesus Christ of Latter-day Saints. "
     "Members are happy to be called Latter-day Saints or members of the Church of Jesus Christ. The Book of Mormon "
     "keeps its name.</p>"),
    ("What do Latter-day Saints believe?",  # what do mormons believe 24,000; what is a mormon 11,000
     "<p>Latter-day Saints worship God the Father and His Son, Jesus Christ. They believe the Church Christ organized "
     "in the New Testament was restored through the Prophet Joseph Smith in the 1800s, and that God still calls "
     "prophets today. They study the Bible and the Book of Mormon together, and they believe families can stay "
     "together after death through promises made in temples.</p>"),
    ("Do Latter-day Saints believe in Jesus? Are they Christians?",  # do mormons believe in jesus 7,100; are mormons christians 7,100
     "<p>Yes. Jesus Christ's name is in the Church's name, and members pray, take the sacrament and seek forgiveness in "
     "His name. They believe He is the Son of God and the Savior of the world. Some Christian denominations do not "
     "classify the Church as Christian, chiefly over the nature of God and the Nicene Creed, which Latter-day Saints "
     "do not accept.</p>"),
    ("Do Latter-day Saints believe in the Trinity?",  # do mormons believe in the trinity 2,800
     "<p>Latter-day Saints believe in God the Father, His Son Jesus Christ, and the Holy Ghost as three separate beings "
     "who are perfectly united in purpose. They call this the Godhead. The traditional Trinity of the Nicene Creed "
     "describes one being in three persons, which is where the two views part ways.</p>"),
    ("What is the Book of Mormon, and who wrote it?",  # what is the book of mormon 2,700; who wrote the book of mormon 2,600
     "<p>The Book of Mormon is a volume of scripture that Latter-day Saints read alongside the Bible. It tells of "
     "ancient peoples in the Americas and of the resurrected Jesus Christ visiting them. Members believe ancient "
     "prophets wrote it, a prophet named Mormon abridged it, and Joseph Smith translated it by the power of God. "
     "It was first published in 1830.</p>"),
    ("Why don't Latter-day Saints drink coffee? Can they have caffeine?",  # why can't mormons drink coffee 5,900; can mormons have caffeine 4,600
     "<p>The Church's health code, the Word of Wisdom (Doctrine and Covenants 89), asks members to avoid alcohol, "
     "tobacco, coffee, tea and harmful or addictive drugs. Church leaders have explained that the revelation's "
     "\"hot drinks\" means coffee and tea, so iced coffee is still coffee. Caffeine itself is not named, so a "
     "caffeinated soda is a personal choice.</p>"),
    ("Do Latter-day Saints drink alcohol?",  # do mormons drink alcohol 2,600
     "<p>No. Alcohol is part of the Word of Wisdom, so Latter-day Saints do not drink it, and institute activities "
     "are alcohol-free.</p>"),
    ("Do Latter-day Saints have multiple wives?",  # do mormons have multiple wives 4,600
     "<p>No. Some early members practiced plural marriage in the 1800s, and the Church ended the practice in 1890. "
     "Anyone who practices it today is excommunicated, and groups that still do are separate from the Church.</p>"),
    ("Do Latter-day Saints celebrate Christmas and Easter?",  # do mormons celebrate christmas 4,800; easter 2,900
     "<p>Yes, both. Christmas centers on the birth of Jesus Christ and Easter on His Resurrection. Wards hold "
     "Christmas programs and Easter Sunday services, and families keep the same holiday traditions as their "
     "neighbors.</p>"),
    ("What are temple garments?",  # what are mormon garments 2,100
     "<p>Adult members who have made promises in the temple wear a simple white undergarment beneath their everyday "
     "clothes. It reminds them of those promises and of Jesus Christ. Members treat garments as sacred and keep them "
     "out of view.</p>"),
    ("Is there a temple in Arkansas?",  # bentonville arkansas temple 700
     "<p>Yes. The Bentonville Arkansas Temple, the first in the state, was dedicated on September 17, 2023. Anyone may "
     "attend Sunday services at a meetinghouse. Temples are reserved for ordinances such as eternal marriage, for "
     "members who hold a temple recommend.</p>"),
    ("Where does the Church of Jesus Christ meet near me in central Arkansas?",  # lds church near me 78,000; mormon church near me 55,000
     f"<p>The two stakes have {UNIT_COUNT} wards and branches meeting in Little Rock, North Little Rock, Conway, "
     "Quitman, Morrilton, Russellville, Danville, Hot Springs, Pine Bluff, Malvern, Arkadelphia, Glenwood, Hope, "
     "Camden and Monticello. Sunday services are open to everyone. The "
     "<a href=\"index.html#stakes\">stake tabs on the home page</a> list each one.</p>"),
]

FAQ_TEASER = [FAQ_INSTITUTE[2], FAQ_INSTITUTE[3], FAQ_INSTITUTE[4], FAQ_INSTITUTE[6]]


def details(items):
    return "\n".join(
        f'<details><summary>{esc(q)}</summary><div class="answer">{a}</div></details>' for q, a in items
    )


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def ld_script(obj):
    return f'<script type="application/ld+json">{json.dumps(obj)}</script>'


POSTAL = {
    "@type": "PostalAddress",
    "streetAddress": ADDRESS["street"],
    "addressLocality": ADDRESS["city"],
    "addressRegion": ADDRESS["state"],
    "postalCode": ADDRESS["zip"],
    "addressCountry": "US",
}


def head(title, desc, path, image, nav, extra_ld="", body_class=""):
    links = "\n      ".join(
        f'<a href="{href}"{" aria-current=" + chr(34) + "page" + chr(34) if href == path else ""}>{label}</a>'
        for label, href in nav
    )
    return f"""<!doctype html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="noindex, nofollow">
<link rel="canonical" href="{SITE}{path if path != 'index.html' else ''}">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}images/{image}-1400.webp">
<meta name="theme-color" content="#173226">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preload" href="fonts/source-serif-4-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/source-sans-3-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="styles.css">
<script>document.documentElement.className='js'</script>
{extra_ld}
</head>
<body{(' class="' + body_class + '"') if body_class else ""}>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="index.html">{icon('book', 28)}<span>{NAME}</span></a>
    <nav class="site-nav" aria-label="Main">
      {links}
    </nav>
  </div>
</header>
"""


def foot(cta_href, heading="Bring a friend to institute this Tuesday", label="Plan your first Tuesday"):
    return f"""<section class="final dark" aria-labelledby="final-title">
  <div class="wrap narrow">
    <h2 id="final-title">{heading}</h2>
    <p class="lead">{CLASS_TIME} at {esc(ADDR_SHORT)}. Free for anyone 18 to 35, single or married.</p>
    <a class="btn btn-cream" href="{cta_href}">{label}</a>
  </div>
</section>
</main>
<footer class="site-foot">
  <div class="wrap foot-grid">
    <div>
      <p class="foot-name">{NAME}</p>
      <address style="font-style:normal">Little Rock Stake class, {CLASS_TIME}<br>{esc(ADDRESS['street'])}<br>{esc(ADDRESS['city'])}, {ADDRESS['state']} {ADDRESS['zip']}</address>
      <p style="margin-top:14px">An independent site for young adults in the Little Rock Arkansas Stake and the North Little Rock Arkansas Stake. It is not owned or sponsored by The Church of Jesus Christ of Latter-day Saints.</p>
    </div>
    <ul class="foot-links">
      <li><a href="index.html#stakes">Stakes and wards</a></li>
      <li><a href="little-rock.html">Little Rock Stake class</a></li>
      <li><a href="faq.html">FAQ</a></li>
      <li><a href="new-to-the-church.html">New to the Church?</a></li>
    </ul>
  </div>
</footer>
<script>
(function(){{
  var tabs=[].slice.call(document.querySelectorAll('[role="tab"]'));
  function show(t,focus){{
    tabs.forEach(function(x){{
      var on=x===t;x.setAttribute('aria-selected',on);x.tabIndex=on?0:-1;
      document.getElementById(x.getAttribute('aria-controls')).hidden=!on;
    }});
    if(focus)t.focus();
  }}
  tabs.forEach(function(t,i){{
    t.addEventListener('click',function(){{show(t);history.replaceState(null,'','#'+t.dataset.hash)}});
    t.addEventListener('keydown',function(e){{
      var n=null;
      if(e.key==='ArrowRight')n=tabs[(i+1)%tabs.length];
      if(e.key==='ArrowLeft')n=tabs[(i-1+tabs.length)%tabs.length];
      if(e.key==='Home')n=tabs[0];
      if(e.key==='End')n=tabs[tabs.length-1];
      if(n){{e.preventDefault();show(n,true)}}
    }});
  }});
  if(tabs.length){{
    var h=location.hash.slice(1),start=tabs.filter(function(t){{return t.dataset.hash===h}})[0]||tabs[0];
    show(start);
    if(start.dataset.hash===h)document.getElementById('stakes').scrollIntoView();
  }}
  var els=document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){{
    var io=new IntersectionObserver(function(es){{es.forEach(function(e){{if(e.isIntersecting){{e.target.classList.add('in');io.unobserve(e.target)}}}})}},{{rootMargin:'0px 0px -8% 0px'}});
    els.forEach(function(el){{io.observe(el)}});
  }}else{{els.forEach(function(el){{el.classList.add('in')}})}}
}})();
</script>
</body>
</html>
"""


def picture(name, alt, widths, sizes, w, h, eager=False):
    srcset = ", ".join(f"images/{name}-{x}.webp {x}w" for x in widths)
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return (f'<img src="images/{name}-{widths[0]}.webp" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{h}" alt="{esc(alt)}" {load}>')


def unit_list(units):
    return '<ul class="unit-list">' + "".join(
        f'<li class="unit"><span class="unit-name">{esc(n)}</span>'
        f'<span class="unit-addr">Meets in {esc(a.rsplit(", ", 1)[-1])}</span></li>'
        for n, t, a in units
    ) + "</ul>"


def stake_tabs():
    tabs, panels = [], []
    for i, s in enumerate(STAKES):
        tabs.append(
            f'<button class="tab" role="tab" id="tab-{s["id"]}" aria-controls="panel-{s["id"]}" '
            f'aria-selected="{"true" if i == 0 else "false"}" data-hash="{s["id"]}">'
            f'<span class="tab-name">{s["name"]}</span><span class="tab-sub">{esc(s["sub"])}</span></button>'
        )
        facts = "".join(f"<li>{icon(k, 22)}<span>{esc(v)}</span></li>" for k, v in s["facts"])
        if s["page"]:
            buttons = (f'<a class="btn btn-cream" href="{s["page"]}">See the Little Rock class</a>'
                       '<p class="card-link"><a href="#register">How to register</a></p>')
        else:
            buttons = '<a class="btn btn-cream" href="#register">How to register</a>'
        panels.append(f"""<div class="panel" role="tabpanel" id="panel-{s['id']}" aria-labelledby="tab-{s['id']}" tabindex="0">
  <div class="panel-grid">
    <div class="class-card">
      <h3>{s['class_title']}</h3>
      <ul class="class-facts">{facts}</ul>
      <p>{esc(s['class_note'])}</p>
      {buttons}
    </div>
    <div>
      <div class="dir-head"><h3>Wards and branches</h3><span>{len(s['units'])} units</span></div>
      {unit_list(s['units'])}
    </div>
  </div>
</div>""")
    return (f'<div class="tabs"><div class="tablist" role="tablist" aria-label="Stakes">{"".join(tabs)}</div>'
            + "\n".join(panels) + "</div>")


PROBLEM_CARDS = """
      <div class="card reveal">
        <div class="icon">{pin}</div>
        <h3>{h1}</h3>
        <p>{p1}</p>
      </div>
      <div class="card reveal">
        <div class="icon">{person}</div>
        <h3>Lonelier than anyone lets on</h3>
        <p>61 percent of Americans ages 18 to 25 reported serious loneliness in a national survey. Sitting in a family ward as one of the only single adults can sharpen that on a Sunday.</p>
        <span class="cite">Harvard Graduate School of Education, Making Caring Common, "Loneliness in America," 2021</span>
      </div>
      <div class="card reveal">
        <div class="icon">{heart}</div>
        <h3>Nobody should work out their faith alone</h3>
        <p>Questions about the scriptures, dating, school, work and doubt deserve a room full of people asking the same ones.</p>
      </div>"""


def problem_cards(h1, p1):
    return PROBLEM_CARDS.format(pin=icon("pin"), person=icon("person"), heart=icon("heart"), h1=h1, p1=p1)


def register_steps(step1, step3):
    return f"""<ol class="steps">
      <li class="reveal"><div class="icon">{icon('map')}</div><h3>{step1[0]}</h3><p>{step1[1]}</p></li>
      <li class="reveal"><div class="icon">{icon('pencil')}</div><h3>Sign up on myInstitute</h3><p>Go to <span class="url">myinstitute.churchofjesuschrist.org</span> and search for Little Rock. Members sign in with a Church account. Friends of other faiths can use Quick Signup with a name, an email and a birthdate.</p></li>
      <li class="reveal"><div class="icon">{icon('calendar')}</div><h3>{step3[0]}</h3><p>{step3[1]}</p></li>
    </ol>"""


def credit_block():
    return f"""<div class="split sub-block">
      <div>
        <h3 style="font-size:1.5rem">Earning institute credit</h3>
        <p>Credit counts toward institute graduation and, at many Church schools, toward religion requirements. To earn it:</p>
        <ul class="check-list">
          <li>Attend at least 75 percent of class meetings.</li>
          <li>Finish the assigned reading: all of it for scripture courses, 75 percent for other courses.</li>
          <li>Complete the course's learning experiences.</li>
        </ul>
        <p class="small">BYU, BYU-Idaho, BYU-Hawaii and Ensign College each set their own transfer rules.</p>
      </div>
      <div class="photo">
        {picture('notes', 'A young woman reading a book at a wooden picnic table', [800, 1200], '(max-width: 820px) 100vw, 540px', 1200, 800)}
      </div>
    </div>"""


def success_block():
    return f"""<section class="band" aria-labelledby="success-title">
  <div class="wrap">
    <div class="split">
      <div>
        <h2 id="success-title">Tuesday nights with people who share your faith</h2>
        <p>A year of institute in central Arkansas adds up to:</p>
        <ul class="icon-list">
          <li><span class="icon">{icon('people', 22)}</span><span>Friends from Little Rock to Hot Springs who know your name</span></li>
          <li><span class="icon">{icon('book', 22)}</span><span>A scripture habit that outlasts the semester</span></li>
          <li><span class="icon">{icon('question', 22)}</span><span>Room to ask the questions you have been carrying around</span></li>
        </ul>
        <p class="small">Without a class, too many young adults drift through their twenties alone, one quiet Sunday at a time.</p>
      </div>
      <div class="photo">
        {picture('friends', 'A group of young adults talking and laughing on a set of stone steps', [800, 1400], '(max-width: 820px) 100vw, 540px', 1400, 933)}
      </div>
    </div>
  </div>
</section>"""


def faq_teaser(items):
    return f"""<section id="faq" aria-labelledby="faq-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="faq-title">Questions young adults ask first</h2>
    </div>
    <div class="faq-list">
      {details(items)}
    </div>
    <div class="cta-row"><a class="btn btn-line" href="faq.html">Read all questions</a></div>
  </div>
</section>
"""


COURSES = f"""<div class="sub-block">
      <h3>Courses taught in institute</h3>
      <p class="small">Each semester's course is listed on myInstitute.</p>
      <div class="cards four">
        <div class="card reveal"><div class="icon">{icon('book')}</div><h3>Jesus Christ and the Everlasting Gospel</h3><p>The life, mission and Atonement of the Savior, studied through the scriptures.</p></div>
        <div class="card reveal"><div class="icon">{icon('book')}</div><h3>Foundations of the Restoration</h3><p>Joseph Smith, the Doctrine and Covenants and the history of the restored Church.</p></div>
        <div class="card reveal"><div class="icon">{icon('book')}</div><h3>Teachings and Doctrine of the Book of Mormon</h3><p>The doctrines at the center of the Book of Mormon and how to live them.</p></div>
        <div class="card reveal"><div class="icon">{icon('book')}</div><h3>The Eternal Family</h3><p>Marriage, dating and family, grounded in the family proclamation.</p></div>
      </div>
    </div>"""


def index():
    ld = {
        "@context": "https://schema.org",
        "@type": "EducationalOrganization",
        "name": NAME,
        "url": SITE,
        "description": "Weekly Institute of Religion classes for young adults ages 18 to 35 in the Little Rock and North Little Rock stakes.",
        "address": POSTAL,
        "areaServed": ["Little Rock, AR", "North Little Rock, AR", "Conway, AR", "Benton, AR", "Hot Springs, AR"],
    }
    nav = [("Stakes", "index.html#stakes"), ("Little Rock class", "little-rock.html"), ("Register", "index.html#register"), ("FAQ", "faq.html")]
    out = head(
        "Institute Classes in Little Rock and North Little Rock | Arkansas YSA Institute",
        "Free weekly institute classes for young adults 18 to 35 in the Little Rock and North Little Rock stakes. "
        "Class time and address, every ward and branch, and how to register on myInstitute.",
        "index.html", "hero", nav, ld_script(ld),
    )
    out += f"""<main id="main">
<section class="hero" aria-labelledby="hero-title">
  <div class="wrap narrow">
    <h1 id="hero-title">Institute classes for young adults in Little Rock and North Little Rock</h1>
    <p class="lead">Free weekly gospel study for anyone 18 to 35 in central Arkansas, single or married, members of The Church of Jesus Christ of Latter-day Saints and friends of other faiths alike.</p>
    <div class="cta-row">
      <a class="btn" href="#stakes">Find your class</a>
      <p class="small">Little Rock Stake class: {CLASS_TIME} at {esc(ADDR_LINE)}</p>
    </div>
  </div>
  <div class="hero-photo">
    {picture('hero', 'Two young women laughing together on the grass with their scriptures open', [800, 1400], '(max-width: 1180px) 100vw, 1180px', 1400, 787, eager=True)}
  </div>
</section>

<section id="stakes" class="band" aria-labelledby="stakes-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="stakes-title">Institute and wards in both central Arkansas stakes</h2>
      <p class="lead">{UNIT_COUNT} wards and branches make up the two stakes, from Danville and Russellville down to Hope and Monticello. Each tab shows the stake's institute class and every ward and branch in it.</p>
    </div>
    {stake_tabs()}
    <p class="dir-note center">Not sure which unit is yours? The meetinghouse locator on the Church's website shows each boundary.</p>
  </div>
</section>

<section aria-labelledby="problem-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="problem-title">Being a young single adult in Arkansas can be lonely</h2>
      <p class="lead">Utah has a YSA ward on every other corner. Central Arkansas has long drives and small congregations.</p>
    </div>
    <div class="cards">{problem_cards(f"Spread across {UNIT_COUNT} congregations", "Young adults in the two stakes are scattered over a couple hundred miles of highway, and many wards and branches have only a handful of them.")}
    </div>
  </div>
</section>

<section id="classes" class="band" aria-labelledby="classes-title">
  <div class="wrap">
    <div class="split photo-left">
      <div class="photo tall">
        {picture('study', 'Two young women sitting on the grass reading their scriptures together', [800, 1200], '(max-width: 820px) 100vw, 540px', 1200, 1500)}
      </div>
      <div>
        <h2 id="classes-title">A weekly class made for the years between 18 and 35</h2>
        <p>Institute began in 1926 in Moscow, Idaho, for college students who wanted their faith to keep pace with their schooling. Today the Church's Seminaries and Institutes of Religion holds classes in nearly 2,700 locations, from campus buildings to living rooms.</p>
        <p>Classes lean on discussion, and teachers are local members called by the stake. The Little Rock Stake class meets on Tuesday nights in a home in Benton.</p>
        <div class="facts-row">
          <div class="fact"><strong>18 to 35</strong><span>single or married</span></div>
          <div class="fact"><strong>$0</strong><span>for every course</span></div>
          <div class="fact"><strong>7 PM</strong><span>Tuesday nights</span></div>
        </div>
      </div>
    </div>
    {COURSES}
  </div>
</section>

<section id="register" aria-labelledby="register-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="register-title">Join a class in three steps</h2>
      <p class="lead">Members and friends of other faiths sign up the same way, and you can visit a class before you register.</p>
    </div>
    {register_steps(("Pick your stake", 'Open the <a href="#stakes">stake tabs</a> and find the class nearest where you live, work or study.'), ("Come Tuesday night", f"Bring scriptures or the Gospel Library app to {esc(ADDR_SHORT)} {CLASS_TIME_PHRASE}."))}
    <div class="cta-row"><a class="btn" href="little-rock.html">See the Little Rock class</a></div>
    {credit_block()}
  </div>
</section>

{success_block()}

{faq_teaser(FAQ_TEASER)}"""
    out += foot("little-rock.html#visit")
    return out


ICS_FILE = "little-rock-institute.ics"

# Upcoming events. Times are Central. Past events drop off at build time and in the browser.
EVENTS = [
    {"slug": "ysa-devotional-2026-11-01", "date": "2026-11-01", "start": "190000", "end": "200000", "time": "7:00 PM",
     "title": "Worldwide Devotional for Young Adults",
     "place": "Live broadcast on Gospel Library and the Church's YouTube channel",
     "note": "Elder Quentin L. Cook of the Quorum of the Twelve Apostles speaks, with Sister Mary G. Cook."},
    {"slug": "christmas-devotional-2026-12-06", "date": "2026-12-06", "start": "190000", "end": "200000", "time": "7:00 PM",
     "title": "First Presidency's Christmas Devotional",
     "place": "Broadcast on Gospel Library and the Church's YouTube channel",
     "note": "Music and messages about the birth of Jesus Christ from the First Presidency."},
]
BUILD_DATE = "2026-10-23"


def event_ics(e):
    loc = e["place"].replace(",", "\\,")
    day = e["date"].replace("-", "")
    return "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Arkansas YSA Institute//Events//EN", "CALSCALE:GREGORIAN",
        "BEGIN:VEVENT", f"UID:{e['slug']}@odyssey-jotun.github.io", "DTSTAMP:20261023T000000Z",
        f"DTSTART;TZID=America/Chicago:{day}T{e['start']}", f"DTEND;TZID=America/Chicago:{day}T{e['end']}",
        f"SUMMARY:{e['title']}", f"LOCATION:{loc}", f"DESCRIPTION:{e['note']}",
        "END:VEVENT", "END:VCALENDAR", ""])


def events_section():
    import datetime as dt
    rows = [f"""<li class="event">
        <div class="event-date" aria-hidden="true"><span class="ev-small">Every</span><span class="ev-big">Tue</span><span class="ev-small">7 PM</span></div>
        <div class="event-body">
          <h3>Institute class</h3>
          <p class="ev-meta">{CLASS_TIME}, {esc(ADDR_SHORT)}</p>
          <p>Bring scriptures or the Gospel Library app, and bring a friend.</p>
          <a class="ev-link" href="{ICS_FILE}" download>Add to calendar</a>
        </div>
      </li>"""]
    for e in EVENTS:
        if e["date"] < BUILD_DATE:
            continue
        d = dt.date.fromisoformat(e["date"])
        rows.append(f"""<li class="event" data-date="{e['date']}">
        <div class="event-date" aria-hidden="true"><span class="ev-small">{d.strftime('%b')}</span><span class="ev-big">{d.day}</span><span class="ev-small">{d.strftime('%a')}</span></div>
        <div class="event-body">
          <h3>{esc(e['title'])}</h3>
          <p class="ev-meta"><time datetime="{e['date']}">{d.strftime('%A, %B')} {d.day}</time>, {e['time']} Central. {esc(e['place'])}</p>
          <p>{esc(e['note'])}</p>
          <a class="ev-link" href="events/{e['slug']}.ics" download>Add to calendar</a>
        </div>
      </li>""")
    return f"""<section id="events" aria-labelledby="events-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="events-title">Upcoming events</h2>
      <p class="lead">Class every Tuesday, plus the Church broadcasts made for young adults.</p>
    </div>
    <ul class="events">
      {''.join(rows)}
    </ul>
  </div>
</section>
<script>
(function(){{var t=new Date();t.setHours(0,0,0,0);document.querySelectorAll('.event[data-date]').forEach(function(el){{var p=el.dataset.date.split('-');if(new Date(+p[0],p[1]-1,+p[2])<t)el.remove()}})}})();
</script>"""


def ics():
    loc = ADDR_LINE.replace(",", "\\,")
    return "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Arkansas YSA Institute//Little Rock Stake//EN", "CALSCALE:GREGORIAN",
        "BEGIN:VTIMEZONE", "TZID:America/Chicago",
        "BEGIN:DAYLIGHT", "TZOFFSETFROM:-0600", "TZOFFSETTO:-0500", "TZNAME:CDT", "DTSTART:19700308T020000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=2SU", "END:DAYLIGHT",
        "BEGIN:STANDARD", "TZOFFSETFROM:-0500", "TZOFFSETTO:-0600", "TZNAME:CST", "DTSTART:19701101T020000", "RRULE:FREQ=YEARLY;BYMONTH=11;BYDAY=1SU", "END:STANDARD",
        "END:VTIMEZONE",
        "BEGIN:VEVENT", "UID:little-rock-stake-institute@odyssey-jotun.github.io", "DTSTAMP:20261023T000000Z",
        "DTSTART;TZID=America/Chicago:20261027T190000", "DTEND;TZID=America/Chicago:20261027T200000",
        "RRULE:FREQ=WEEKLY;BYDAY=TU",
        "SUMMARY:Institute at Marc and Nikki's", f"LOCATION:{loc}",
        "DESCRIPTION:Little Rock Stake institute class. Bring scriptures or the Gospel Library app\\, and bring a friend.",
        "END:VEVENT", "END:VCALENDAR", ""])


def visit_media():
    if HOUSE_PHOTO:
        return (f'<figure class="photo house">{picture("house", "The red brick house at " + ADDR_SHORT + " where the class meets", [800, 858], "(max-width: 820px) 100vw, 540px", 858, 572)}'
                '<figcaption>Look for the red brick house with the crape myrtle out front.</figcaption></figure>')
    return f"""<div class="sign-wrap" role="img" aria-label="Street sign for Millbrook Drive with house number {ADDRESS['street'].split()[0]}">
        <div class="street-sign">Millbrook Dr</div>
        <div class="sign-post" aria-hidden="true"></div>
        <div class="house-number">{ADDRESS['street'].split()[0]}</div>
      </div>"""


def little_rock():
    ld = {
        "@context": "https://schema.org",
        "@type": "EducationalOrganization",
        "name": "Little Rock Stake Institute",
        "url": SITE + "little-rock.html",
        "description": f"Weekly Institute of Religion class for young adults ages 18 to 35 in the Little Rock Arkansas Stake, {CLASS_TIME} in Benton.",
        "address": POSTAL,
        "areaServed": ["Little Rock, AR", "Benton, AR", "Bryant, AR", "Hot Springs, AR", "Pine Bluff, AR", "Malvern, AR", "Arkadelphia, AR"],
    }
    nav = [("Where we meet", "little-rock.html#visit"), ("Events", "little-rock.html#events"), ("First Tuesday", "little-rock.html#first-tuesday"), ("FAQ", "faq.html")]
    extra = (ld_script(ld) + '\n<link rel="preload" href="fonts/caveat-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>')
    out = head(
        "Little Rock Stake Institute, Tuesdays at 7 PM in Benton | Arkansas YSA Institute",
        f"Institute for young adults 18 to 35 in the Little Rock Arkansas Stake, {CLASS_TIME} at Marc and Nikki's home, "
        f"{ADDR_LINE}. Free, friends welcome.",
        "little-rock.html", "ysa-home", nav, extra, body_class="warm",
    )
    out += f"""<main id="main">
<section class="hero split-hero" aria-labelledby="hero-title">
  <div class="wrap">
    <div class="split">
      <div class="hero-copy">
        <h1 id="hero-title">Institute night for young adults in the Little Rock Stake</h1>
        <p class="lead">Every Tuesday at 7, young single and married adults ages 18 to 35 gather in a home in Benton to study the gospel and make friends from across the stake. Members and friends of other faiths are welcome.</p>
        <div class="cta-row">
          <a class="btn" href="#visit">Come this Tuesday</a>
          <p class="small">7:00 PM at {esc(ADDR_LINE)}</p>
        </div>
      </div>
      <div class="photo hero-side">
        {picture('ysa-home', 'Six young adults smiling together on a yellow couch in a living room', [800, 1400, 2100], '(max-width: 820px) 100vw, 560px', 1400, 840, eager=True)}
      </div>
    </div>
  </div>
</section>

<section class="band" aria-labelledby="problem-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="problem-title">Young adults in the Little Rock Stake are spread thin</h2>
      <p class="lead">Eleven wards and branches stretch from Pinnacle Mountain to Monticello.</p>
    </div>
    <div class="soft-points">
      <div class="reveal"><div class="icon">{icon('pin')}</div><h3>A lot of highway between friends</h3><p>Young adults are scattered across central and south Arkansas, and many branches have only a handful of them.</p></div>
      <div class="reveal"><div class="icon">{icon('person')}</div><h3>Lonelier than anyone lets on</h3><p>In a Harvard survey, 61 percent of Americans ages 18 to 25 reported serious loneliness (Making Caring Common, 2021). Sunday in a family ward can make that sharper.</p></div>
      <div class="reveal"><div class="icon">{icon('heart')}</div><h3>Faith grows better in company</h3><p>Questions about the scriptures, dating, school, work and doubt deserve a living room full of people asking the same ones.</p></div>
    </div>
  </div>
</section>

<section id="welcome" aria-labelledby="welcome-title">
  <div class="wrap">
    <div class="split photo-left welcome">
      <div class="photo tall hosts">
        {picture('hosts', 'Marc and Nikki, who host the Little Rock Stake institute class in their home, smiling together', [800, 1200], '(max-width: 820px) 100vw, 480px', 1200, 1500)}
      </div>
      <div class="letter">
        <h2 id="welcome-title">Hi, we're Marc and Nikki</h2>
        <p>Every Tuesday at 7, we open our home in Benton for the Little Rock Stake's institute class.</p>
        <p>Whether you're coming straight from work, driving in from Hot Springs or Pine Bluff, or opening the Book of Mormon for the first time, you're welcome here. Single, married, member or friend of another faith, if you're 18 to 35, this class is for you.</p>
        <p>Bring your scriptures or the Gospel Library app, and bring a friend if you like. We'll save you a seat.</p>
        <p class="sig">Marc &amp; Nikki</p>
      </div>
    </div>
  </div>
</section>

<section id="visit" class="band" aria-labelledby="visit-title">
  <div class="wrap">
    <div class="split">
      <div>
        <h2 id="visit-title">Tuesday nights at 7 on Millbrook Drive</h2>
        <p class="address-big">{esc(ADDRESS['street'])}<br>{esc(ADDRESS['city'])}, {ADDRESS['state']} {ADDRESS['zip']}</p>
        <ul class="icon-list">
          <li><span class="icon">{icon('clock', 22)}</span><span>Every Tuesday at 7:00 PM</span></li>
          <li><span class="icon">{icon('home', 22)}</span><span>Our home, about 25 miles southwest of downtown Little Rock</span></li>
          <li><span class="icon">{icon('book', 22)}</span><span>Bring scriptures or the Gospel Library app</span></li>
          <li><span class="icon">{icon('people', 22)}</span><span>Free for anyone 18 to 35, and friends are welcome</span></li>
        </ul>
      </div>
      {visit_media()}
    </div>
    <div class="cta-row"><a class="btn" href="{ICS_FILE}" download>Add Tuesdays to your calendar</a></div>
  </div>
</section>

{events_section()}

<section id="first-tuesday" class="band" aria-labelledby="first-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="first-title">Your first Tuesday</h2>
      <p class="lead">Three small steps, and the first one can wait until after your visit.</p>
    </div>
    <ol class="steps soft">
      <li class="reveal"><div class="icon">{icon('pencil')}</div><h3>Sign up on myInstitute</h3><p>Search <span class="url">myinstitute.churchofjesuschrist.org</span> for Little Rock. Friends of other faiths can use Quick Signup with just a name, an email and a birthdate.</p></li>
      <li class="reveal"><div class="icon">{icon('calendar')}</div><h3>Save the date</h3><p>Add Tuesdays at 7 to your calendar so the week doesn't swallow it.</p></li>
      <li class="reveal"><div class="icon">{icon('home')}</div><h3>Knock on the door</h3><p>Come to {esc(ADDRESS['street'])} with your scriptures or your phone, and bring a friend if you like.</p></li>
    </ol>
    <div class="cta-row"><a class="btn" href="{ICS_FILE}" download>Add Tuesdays to your calendar</a></div>
  </div>
</section>

<section aria-labelledby="success-title">
  <div class="wrap">
    <div class="split photo-left">
      <div class="photo tall">
        {picture('study', 'Two young women sitting on the grass reading their scriptures together', [800, 1200], '(max-width: 820px) 100vw, 540px', 1200, 1500)}
      </div>
      <div>
        <h2 id="success-title">Tuesday nights with people who share your faith</h2>
        <p>A year of Tuesdays adds up to:</p>
        <ul class="icon-list">
          <li><span class="icon">{icon('people', 22)}</span><span>Friends from Little Rock to Hot Springs who know your name</span></li>
          <li><span class="icon">{icon('book', 22)}</span><span>A scripture habit that outlasts the semester</span></li>
          <li><span class="icon">{icon('question', 22)}</span><span>Room to ask the questions you have been carrying around</span></li>
        </ul>
        <p class="small">Without a class, too many young adults drift through their twenties alone, one quiet Sunday at a time.</p>
      </div>
    </div>
  </div>
</section>

<section id="wards" class="band" aria-labelledby="wards-title">
  <div class="wrap">
    <div class="section-head">
      <h2 id="wards-title">Every ward and branch in the stake is welcome</h2>
      <p class="lead">Institute is open to young adults from all eleven.</p>
    </div>
    <div class="ward-panel">
      {unit_list(LR_UNITS)}
    </div>
    <p class="dir-note center">Live north of the river? See the <a href="index.html#north-little-rock-stake">North Little Rock Stake</a>.</p>
  </div>
</section>

{faq_teaser([FAQ_WHEN] + FAQ_TEASER).replace('Questions young adults ask first', 'Questions people ask before their first Tuesday')}"""
    out += foot("#visit", heading="We'll save you a seat", label="Plan your first Tuesday")
    return out


def faq_ld(items):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
            for q, a in items
        ],
    }


def faq():
    nav = [("Stakes", "index.html#stakes"), ("Little Rock class", "little-rock.html"), ("Register", "index.html#register"), ("FAQ", "faq.html")]
    out = head(
        "Institute FAQ: Classes, myInstitute and YSA Wards | Arkansas YSA Institute",
        "Answers about institute classes, myInstitute registration, credit and YSA wards for young adults in the "
        "Little Rock and North Little Rock stakes.",
        "faq.html", "faq", nav, ld_script(faq_ld(FAQ_INSTITUTE)),
    )
    out += f"""<main id="main">
<section class="hero" aria-labelledby="hero-title">
  <div class="wrap narrow">
    <h1 id="hero-title">Questions about institute in central Arkansas</h1>
    <p class="lead">Class times, registration, credit and which ward is yours, for young adults in the Little Rock and North Little Rock stakes.</p>
  </div>
  <div class="hero-photo">
    {picture('faq', 'Three young adults talking and smiling outside a building', [800, 1400], '(max-width: 1180px) 100vw, 1180px', 1400, 933, eager=True)}
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="faq-list">
      {details(FAQ_INSTITUTE)}
    </div>
    <p class="dir-note center">New to the Church of Jesus Christ? <a href="new-to-the-church.html">Read answers to common questions about Latter-day Saints.</a></p>
  </div>
</section>
"""
    out += foot("little-rock.html#visit")
    return out


def church_faq():
    nav = [("Stakes", "index.html#stakes"), ("Little Rock class", "little-rock.html"), ("Register", "index.html#register"), ("FAQ", "faq.html")]
    out = head(
        "New to the Church of Jesus Christ? Common Questions | Arkansas YSA Institute",
        "Plain answers to common questions about Latter-day Saints: beliefs about Jesus Christ, the Book of Mormon, "
        "coffee and the Word of Wisdom, temples and where the Church meets in central Arkansas.",
        "new-to-the-church.html", "faq", nav, ld_script(faq_ld(FAQ_CHURCH)),
    )
    out += f"""<main id="main">
<section class="hero" aria-labelledby="hero-title">
  <div class="wrap narrow">
    <h1 id="hero-title">New to the Church of Jesus Christ?</h1>
    <p class="lead">Plain answers to the questions friends of other faiths ask before their first visit.</p>
  </div>
  <div class="hero-photo">
    {picture('faq', 'Three young adults talking and smiling outside a building', [800, 1400], '(max-width: 1180px) 100vw, 1180px', 1400, 933, eager=True)}
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="faq-list">
      {details(FAQ_CHURCH)}
    </div>
  </div>
</section>
"""
    out += foot("little-rock.html#visit")
    return out


if __name__ == "__main__":
    (ROOT / "index.html").write_text(index())
    (ROOT / "little-rock.html").write_text(little_rock())
    (ROOT / "faq.html").write_text(faq())
    (ROOT / "new-to-the-church.html").write_text(church_faq())
    (ROOT / ICS_FILE).write_bytes(ics().encode("utf-8"))
    (ROOT / "events").mkdir(exist_ok=True)
    for e in EVENTS:
        (ROOT / "events" / f"{e['slug']}.ics").write_bytes(event_ics(e).encode("utf-8"))
    print("built index.html, little-rock.html, faq.html", "(house photo)" if HOUSE_PHOTO else "(street sign, no house photo yet)")
