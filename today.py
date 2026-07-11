import datetime as dt
import html
import json
import os
import urllib.request


# Profile README generator inspired by Andrew Grant's setup:
# https://github.com/Andrew6rant/Andrew6rant

API_BASE = "https://api.github.com"
USER_NAME = os.environ.get("USER_NAME", "mateusememe")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "")

SELECTED_WORK = [
    ("transaction.ledger", "AWS ledger"),
    ("fuzzymeans-ai", "AI imputation"),
    ("ai-autopsy-devfest", "Explainable AI"),
    ("codecash", "Spring API"),
]


def github_get(path):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "mateusememe-profile-readme-generator",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"

    request = urllib.request.Request(f"{API_BASE}{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def public_repositories(username):
    repositories = []
    page = 1
    while True:
        data = github_get(
            f"/users/{username}/repos?per_page=100&page={page}&sort=pushed&type=owner"
        )
        if not data:
            return repositories
        repositories.extend(data)
        page += 1


def account_age(created_at):
    created = dt.date.fromisoformat(created_at[:10])
    today = dt.datetime.now(dt.timezone.utc).date()

    years = today.year - created.year
    months = today.month - created.month
    days = today.day - created.day

    if days < 0:
        months -= 1
        previous_month = today.replace(day=1) - dt.timedelta(days=1)
        days += previous_month.day

    if months < 0:
        years -= 1
        months += 12

    return f"{years}y {months}m {days}d"


def profile_data(username):
    user = github_get(f"/users/{username}")
    repositories = public_repositories(username)
    owned_active = [
        repo for repo in repositories if not repo.get("fork") and not repo.get("archived")
    ]
    total_stars = sum(repo.get("stargazers_count", 0) for repo in owned_active)

    return {
        "name": user.get("name") or username,
        "public_repos": user.get("public_repos", len(repositories)),
        "followers": user.get("followers", 0),
        "stars": total_stars,
        "age": account_age(user["created_at"]),
    }


def esc(value):
    return html.escape(str(value), quote=False)


def tspan(x, y, text):
    return f'<tspan x="{x}" y="{y}">{text}</tspan>'


def row(y, key, value):
    return (
        f'<tspan x="390" y="{y}" class="muted">. </tspan>'
        f'<tspan class="key">{esc(key)}</tspan>: '
        f'<tspan class="value">{esc(value)}</tspan>'
    )


def work_row(y, name, label):
    return (
        f'<tspan x="390" y="{y}" class="muted">. </tspan>'
        f'<tspan class="key">{esc(name)}</tspan>: '
        f'<tspan class="value">{esc(label)}</tspan>'
    )


def box_line(content=""):
    return f"| {content:<32} |"


def render_svg(theme, data):
    if theme == "dark":
        background = "#0d1117"
        foreground = "#c9d1d9"
        key = "#ffa657"
        value = "#a5d6ff"
        accent = "#7ee787"
        muted = "#8b949e"
        line = "#30363d"
    else:
        background = "#f6f8fa"
        foreground = "#24292f"
        key = "#953800"
        value = "#0a3069"
        accent = "#116329"
        muted = "#6e7781"
        line = "#d0d7de"

    public_repos = data["public_repos"]
    followers = data["followers"]
    stars = data["stars"]
    github_age = data["age"]
    github_summary = f"{public_repos} repos, {followers} followers, {stars} stars"

    left = [
        (34, "+-- /home/mateus/profile.json ----+"),
        (54, box_line("{")),
        (74, box_line('"name": "Mateus",')),
        (94, box_line('"role": "Software Engineer",')),
        (114, box_line('"company": "Itau Unibanco",')),
        (134, box_line('"country": "Brazil",')),
        (154, box_line(f'"github_age": "{github_age}",')),
        (174, box_line(f'"public_repos": {public_repos},')),
        (194, box_line(f'"followers": {followers},')),
        (214, box_line(f'"stars": {stars}')),
        (234, box_line("}")),
        (254, "+----------------------------------+"),
        (294, "          ________"),
        (314, "         / ____/ /___  __  ______/ /"),
        (334, "        / /   / / __ \\/ / / / __  / "),
        (354, "       / /___/ / /_/ / /_/ / /_/ /  "),
        (374, "       \\____/_/\\____/\\__,_/\\__,_/   "),
        (414, "+-- current bias ------------------+"),
        (434, "| Data platforms that migrate well |"),
        (454, "| Backend systems that scale.      |"),
        (474, "| AI work that can be explained.   |"),
        (494, "| Cloud systems with observability.|"),
        (514, "+----------------------------------+"),
    ]

    left_text = "\n".join(tspan(24, y, esc(text)) for y, text in left)
    selected_work = "\n".join(
        work_row(y, name, label)
        for y, (name, label) in zip([374, 394, 414, 434], SELECTED_WORK)
    )

    return f"""<?xml version='1.0' encoding='UTF-8'?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="1200px" height="530px" font-size="14px">
<style>
@font-face {{
src: local('Consolas'), local('Consolas Bold');
font-family: 'ConsolasFallback';
font-display: swap;
-webkit-size-adjust: 109%;
size-adjust: 109%;
}}
.key {{fill: {key};}}
.value {{fill: {value};}}
.accent {{fill: {accent};}}
.muted {{fill: {muted};}}
.line {{fill: {line};}}
text, tspan {{white-space: pre;}}
</style>
<rect width="1200px" height="530px" fill="{background}" rx="15"/>
<text x="24" y="34" fill="{foreground}">
{left_text}
</text>
<text x="390" y="34" fill="{foreground}">
<tspan x="390" y="34">mateus@github</tspan><tspan class="line"> -====================-</tspan>
{row(54, "Name", data["name"])}
{row(74, "Role", "Software Engineer @ Itau")}
{row(94, "Education", "MSc CS @ UNESP")}
{row(114, "Location", "Brazil")}
{row(134, "Focus", "Backend, data platforms, cloud")}
{row(154, "GitHub", github_summary)}
<tspan x="390" y="174">- Stack</tspan><tspan class="line"> -====================-</tspan>
{row(194, "Languages.Main", "Python, Go, Java, TS")}
{row(214, "Backend.API", "Spring, Quarkus, Nest, REST")}
{row(234, "Data.Platforms", "Data Mesh, EDD, ETL")}
{row(254, "Messaging", "Kafka, RabbitMQ, Pub/Sub")}
{row(274, "Cloud.Infra", "AWS, GCP, K8s, Docker")}
{row(294, "Storage.Search", "Postgres, MongoDB, Redis")}
{row(314, "Observability", "Datadog, Grafana, X-Ray")}
{row(334, "Architecture", "Hexagonal, Clean, SOLID")}
<tspan x="390" y="354">- Selected Public Work</tspan><tspan class="line"> -==============-</tspan>
{selected_work}
<tspan x="390" y="454" class="muted">. </tspan>
<tspan x="390" y="474">- Contact</tspan><tspan class="line"> -===================-</tspan>
<tspan x="390" y="494" class="muted">. </tspan><tspan class="key">Email</tspan>: <tspan class="value">matt.mendon@gmail.com</tspan>
<tspan x="390" y="514" class="muted">. </tspan><tspan class="key">LinkedIn</tspan>: <tspan class="accent">/in/mateus-men</tspan>
</text>
</svg>
"""


def write_svg(path, content):
    with open(path, "w", encoding="utf-8") as file:
        file.write(content)


if __name__ == "__main__":
    data = profile_data(USER_NAME)
    write_svg("dark_mode.svg", render_svg("dark", data))
    write_svg("light_mode.svg", render_svg("light", data))
    print(
        "Updated SVGs for {user}: {public_repos} repos, {followers} followers, "
        "{stars} stars, account age {age}".format(user=USER_NAME, **data)
    )
