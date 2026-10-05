"""Read the topic map and the open-question titles.

The topic map is the source of truth for which topics exist. The build gives
every topic in it a page: written topics from the content folder, and planned
topics from their entry in the map. engine/format.md describes the map's shape.
"""

import re


def estimate_minutes(size, S):
    """A planned topic's reading time, at the middle of its size band."""
    return round(S.size_midpoint(size) / S.wpm)


def parse_marker_line(line, S):
    """The line under a topic's title: rank | size | cluster | markers."""
    m = S.map
    parts = [p.strip() for p in line.split("|")]
    parts += [""] * (3 - len(parts))
    info = {"rank": parts[0].lower(), "size": parts[1], "cluster": parts[2],
            "read_first_flag": False, "after": [], "updates": [], "ages_fast": False,
            "pilot": False, "markers": parts[3:]}
    for p in parts[3:]:
        low = p.lower()
        if low == m["read_first"].lower():
            info["read_first_flag"] = True
        elif low.startswith(m["after"].lower() + " "):
            info["after"] = S.any_topic_id_re.findall(p)
        elif low.startswith(m["updates"].lower() + " "):
            info["updates"] = S.any_topic_id_re.findall(p)
        elif low == m["ages_fast"].lower():
            info["ages_fast"] = True
        elif low == m["pilot"].lower():
            info["pilot"] = True
    return info


def parse_entry_fields(body_lines):
    """Split a topic entry into its '**Label:** text' fields, in order."""
    fields, cur = [], None
    for line in body_lines:
        m = re.match(r"^\*\*([^*]+?):\*\*\s*(.*)$", line)
        if m:
            cur = [m.group(1).strip(), [m.group(2)]]
            fields.append(cur)
        elif cur is not None:
            cur[1].append(line)
    return [(label, "\n".join(text).strip()) for label, text in fields]


def parse_topic_map(S):
    path = S.file("topic_map")
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    tiers, topics, order = [], {}, []
    tier, group, entry = None, None, None
    reading, quotas = [], {}
    in_reading = False
    names = {t.name: t for t in S.tiers}
    tier_re = re.compile(r"^# (%s)\s*$" % "|".join(re.escape(n) for n in names)) if names else None
    entry_re = re.compile(r"^### (%s) (.+)$" % S.topic_id_pattern)
    rank_line_re = re.compile(r"^(Critical|High|Medium|Context) \|", re.I)
    quota_re = re.compile(r"^\|\s*(%s\d+)\s*\|.*\|\s*(\d+)\s*\|\s*$" % re.escape(S.cluster_prefix))
    order_heading = "## " + S.map["reading_order"]

    def close_entry():
        if entry is not None:
            entry["fields"] = parse_entry_fields(entry.pop("_body"))
            for label, text in entry["fields"]:
                if label.lower() == "why":
                    entry["why"] = text

    in_code = False
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            if entry is not None:
                entry["_body"].append(line)
            continue
        if in_code:
            # An example in a fenced block is never a tier, a topic or a quota. In an entry, it stays text.
            if entry is not None:
                entry["_body"].append(line)
            continue
        q = quota_re.match(line)
        if q and tier is None:
            quotas[q.group(1)] = int(q.group(2))
        if line.startswith(order_heading):
            in_reading = True
            continue
        if in_reading:
            if line.startswith("## ") or line.startswith("# "):
                in_reading = False
            else:
                m = re.match(r"^(\d+)\.\s+(.*)$", line)
                if m:
                    ids = S.any_topic_id_re.findall(m.group(2))
                    note = m.group(2).split(":", 1)[1].strip() if ":" in m.group(2) else ""
                    reading.append({"step": int(m.group(1)), "ids": ids, "note": note})
                continue
        tm = tier_re.match(line) if tier_re else None
        if tm:
            close_entry()
            entry = None
            t = names[tm.group(1)]
            tier = {"key": t.id, "name": t.name, "question": "", "blurb": "", "groups": []}
            tiers.append(tier)
            group = None
            continue
        if tier is None:
            continue
        if not tier["question"] and group is None and entry is None and re.match(r"^\*[^*].*\*$", line.strip()):
            tier["question"] = line.strip().strip("*")
            continue
        gm = re.match(r"^## (.+)$", line)
        if gm:
            close_entry()
            entry = None
            group = {"name": gm.group(1).strip(), "ids": []}
            tier["groups"].append(group)
            continue
        em = entry_re.match(line)
        if em:
            close_entry()
            tid = em.group(1)
            marker = lines[idx + 1] if idx + 1 < len(lines) else ""
            entry = {"id": tid, "title": em.group(2).strip(), "tier": tier["key"],
                     "group": group["name"] if group else "", "why": "", "_body": []}
            entry.update(parse_marker_line(marker, S))
            topics[tid] = entry
            order.append(tid)
            if group is not None:
                group["ids"].append(tid)
            continue
        if entry is not None:
            if line.strip() == "---":
                continue
            if entry["_body"] or line.strip():
                if not (len(entry["_body"]) == 0 and rank_line_re.match(line)):
                    entry["_body"].append(line)
            continue
        if group is None and line.strip() and line.strip() != "---" and not tier["blurb"] and not line.startswith("#"):
            tier["blurb"] = line.strip()
    close_entry()
    # A tier the map doesn't list still gets its page, from the settings.
    present = {t["key"] for t in tiers}
    for t in S.tiers:
        if t.id not in present:
            tiers.append({"key": t.id, "name": t.name, "question": "", "blurb": "", "groups": []})
    by_key = {t["key"]: t for t in tiers}
    tiers = [by_key[t.id] for t in S.tiers]
    for t in tiers:
        st = S.tier_by_id[t["key"]]
        t["question"] = t["question"] or st.question
        t["blurb"] = t["blurb"] or st.definition
    return {"tiers": tiers, "topics": topics, "order": order, "reading": reading, "quotas": quotas}


def parse_questions(S):
    """Open-question IDs and titles only. A question's body can hold private facts
    without tags, so the build never reads it.

    A question opens on a line '**OQ-01. Its title**'. When map.question_groups is set,
    only questions under a '## <that word> ...' heading count, and the heading names
    their group. Otherwise every '##' heading groups the questions under it."""
    path = S.file("open_questions")
    if not path.exists():
        return {}
    word = S.map["question_groups"]
    group_re = re.compile(r"^## (%s.+)$" % (re.escape(word) + r" \d+: " if word else ""))
    q_re = re.compile(r"^\*\*(%s)\. (.+?)\*\*" % S.question_id_pattern)
    questions, group = {}, ""
    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        gm = group_re.match(line)
        if gm:
            group = gm.group(1)
            continue
        if line.startswith("## "):
            group = "" if word else line[3:].strip()
            continue
        qm = q_re.match(line)
        if qm and (group or not word):
            questions[qm.group(1)] = {"id": qm.group(1), "title": qm.group(2).strip(), "group": group}
    return questions
