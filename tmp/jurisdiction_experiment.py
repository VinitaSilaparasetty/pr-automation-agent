#!/usr/bin/env python3
"""
Section IV.D — Jurisdictional Scoping Experiment
Classifies the E1 repo sample by Art. 2 obligation tier.
"""

import json
import re
import subprocess
import base64
import time
from langdetect import detect, LangDetectException

EU_27_NAMES = {
    'austria', 'belgium', 'bulgaria', 'croatia', 'cyprus',
    'czech republic', 'denmark', 'estonia', 'finland', 'france',
    'germany', 'greece', 'hungary', 'ireland', 'italy', 'latvia',
    'lithuania', 'luxembourg', 'malta', 'netherlands', 'poland',
    'portugal', 'romania', 'slovakia', 'slovenia', 'spain', 'sweden'
}

EU_27_CODES = {
    'at', 'be', 'bg', 'hr', 'cy', 'cz', 'dk', 'ee', 'fi', 'fr',
    'de', 'gr', 'hu', 'ie', 'it', 'lv', 'lt', 'lu', 'mt', 'nl',
    'pl', 'pt', 'ro', 'sk', 'si', 'es', 'se'
}

# Major EU cities that may appear without a country name in GitHub location fields
EU_CITY_MAP = {
    # France
    'paris': 'France', 'lyon': 'France', 'marseille': 'France', 'toulouse': 'France',
    'bordeaux': 'France', 'nantes': 'France', 'lille': 'France', 'strasbourg': 'France',
    'brest': 'France', 'rennes': 'France', 'grenoble': 'France', 'montpellier': 'France',
    'nice': 'France', 'nancy': 'France', 'metz': 'France',
    # Germany
    'berlin': 'Germany', 'munich': 'Germany', 'münchen': 'Germany', 'hamburg': 'Germany',
    'frankfurt': 'Germany', 'cologne': 'Germany', 'köln': 'Germany', 'düsseldorf': 'Germany',
    'dortmund': 'Germany', 'essen': 'Germany', 'leipzig': 'Germany', 'bremen': 'Germany',
    'dresden': 'Germany', 'hannover': 'Germany', 'nuremberg': 'Germany', 'nürnberg': 'Germany',
    'stuttgart': 'Germany', 'bonn': 'Germany', 'bielefeld': 'Germany', 'mannheim': 'Germany',
    # Italy
    'rome': 'Italy', 'roma': 'Italy', 'milan': 'Italy', 'milano': 'Italy',
    'naples': 'Italy', 'napoli': 'Italy', 'turin': 'Italy', 'torino': 'Italy',
    'palermo': 'Italy', 'genoa': 'Italy', 'genova': 'Italy', 'bologna': 'Italy',
    'florence': 'Italy', 'firenze': 'Italy', 'venice': 'Italy', 'venezia': 'Italy',
    'verona': 'Italy', 'trieste': 'Italy', 'padova': 'Italy', 'padua': 'Italy',
    # Spain
    'madrid': 'Spain', 'barcelona': 'Spain', 'valencia': 'Spain', 'seville': 'Spain',
    'sevilla': 'Spain', 'zaragoza': 'Spain', 'málaga': 'Spain', 'malaga': 'Spain',
    'bilbao': 'Spain', 'alicante': 'Spain', 'córdoba': 'Spain', 'cordoba': 'Spain',
    # Netherlands
    'amsterdam': 'Netherlands', 'rotterdam': 'Netherlands', 'the hague': 'Netherlands',
    'den haag': 'Netherlands', 'utrecht': 'Netherlands', 'eindhoven': 'Netherlands',
    'groningen': 'Netherlands', 'tilburg': 'Netherlands', 'almere': 'Netherlands',
    # Belgium
    'brussels': 'Belgium', 'bruxelles': 'Belgium', 'brussel': 'Belgium',
    'antwerp': 'Belgium', 'antwerpen': 'Belgium', 'ghent': 'Belgium', 'gent': 'Belgium',
    'liège': 'Belgium', 'liege': 'Belgium', 'bruges': 'Belgium', 'brugge': 'Belgium',
    # Poland
    'warsaw': 'Poland', 'warszawa': 'Poland', 'kraków': 'Poland', 'krakow': 'Poland',
    'łódź': 'Poland', 'lodz': 'Poland', 'wrocław': 'Poland', 'wroclaw': 'Poland',
    'poznań': 'Poland', 'poznan': 'Poland', 'gdańsk': 'Poland', 'gdansk': 'Poland',
    # Sweden
    'stockholm': 'Sweden', 'gothenburg': 'Sweden', 'göteborg': 'Sweden',
    'malmö': 'Sweden', 'malmo': 'Sweden', 'uppsala': 'Sweden', 'linköping': 'Sweden',
    # Portugal
    'lisbon': 'Portugal', 'lisboa': 'Portugal', 'porto': 'Portugal',
    'braga': 'Portugal', 'coimbra': 'Portugal', 'funchal': 'Portugal',
    # Czech Republic
    'prague': 'Czech Republic', 'praha': 'Czech Republic', 'brno': 'Czech Republic',
    'ostrava': 'Czech Republic', 'plzeň': 'Czech Republic', 'plzen': 'Czech Republic',
    # Austria
    'vienna': 'Austria', 'wien': 'Austria', 'graz': 'Austria',
    'linz': 'Austria', 'salzburg': 'Austria', 'innsbruck': 'Austria',
    # Hungary
    'budapest': 'Hungary', 'debrecen': 'Hungary', 'miskolc': 'Hungary',
    # Romania
    'bucharest': 'Romania', 'bucurești': 'Romania', 'cluj': 'Romania',
    'cluj-napoca': 'Romania', 'timișoara': 'Romania', 'timisoara': 'Romania',
    # Greece
    'athens': 'Greece', 'athina': 'Greece', 'thessaloniki': 'Greece',
    'patras': 'Greece', 'heraklion': 'Greece',
    # Denmark
    'copenhagen': 'Denmark', 'københavn': 'Denmark', 'aarhus': 'Denmark',
    'odense': 'Denmark', 'aalborg': 'Denmark',
    # Finland
    'helsinki': 'Finland', 'tampere': 'Finland', 'turku': 'Finland', 'oulu': 'Finland',
    # Ireland
    'dublin': 'Ireland', 'cork': 'Ireland', 'galway': 'Ireland', 'limerick': 'Ireland',
    # Slovakia
    'bratislava': 'Slovakia', 'košice': 'Slovakia', 'kosice': 'Slovakia',
    # Bulgaria
    'sofia': 'Bulgaria', 'plovdiv': 'Bulgaria', 'varna': 'Bulgaria',
    # Croatia
    'zagreb': 'Croatia', 'split': 'Croatia', 'rijeka': 'Croatia',
    # Lithuania
    'vilnius': 'Lithuania', 'kaunas': 'Lithuania', 'klaipėda': 'Lithuania',
    # Latvia
    'riga': 'Latvia', 'daugavpils': 'Latvia',
    # Estonia
    'tallinn': 'Estonia', 'tartu': 'Estonia',
    # Slovenia
    'ljubljana': 'Slovenia', 'maribor': 'Slovenia',
    # Cyprus
    'nicosia': 'Cyprus', 'lefkosia': 'Cyprus', 'limassol': 'Cyprus',
    # Luxembourg
    'luxembourg': 'Luxembourg', 'luxembourg city': 'Luxembourg',
    # Malta
    'valletta': 'Malta', 'birkirkara': 'Malta',
}

EU_OFFICIAL_LANGS = {
    'de', 'fr', 'es', 'it', 'nl', 'pl', 'pt', 'ro', 'sv', 'cs',
    'hu', 'el', 'bg', 'hr', 'da', 'et', 'fi', 'lt', 'lv', 'mt',
    'sk', 'sl', 'ga'
}

EU_CLOUD_RE = re.compile(
    r'eu-west|eu-central|eu-north|europe-west|europe-north', re.I)

EU_DOMAIN_RE = re.compile(
    r'https?://[^\s]*\.(eu|de|fr|nl|it|es|pl|se|be|at|dk|fi|ie|pt'
    r'|cz|hu|ro|sk|bg|hr|lt|lv|ee|si|cy|lu|mt)(/|\s|"|\'|$)', re.I)

GDPR_RE = re.compile(
    r'\bGDPR\b|data protection regulation|General Data Protection|\bDPA\b', re.I)


def gh(endpoint, **params):
    cmd = ['gh', 'api', endpoint]
    for k, v in params.items():
        cmd += ['-f', f'{k}={v}']
    r = subprocess.run(cmd, capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else None


def file_content(owner, repo, path):
    data = gh(f'repos/{owner}/{repo}/contents/{path}')
    if not data or 'content' not in data:
        return None
    try:
        return base64.b64decode(data['content']).decode('utf-8', errors='ignore')
    except Exception:
        return None


def tier1(owner):
    data = gh(f'users/{owner}') or gh(f'orgs/{owner}')
    if not data:
        return False, None
    loc = (data.get('location') or '').strip()
    loc_lower = loc.lower()
    if not loc_lower:
        return False, None
    # Country name substring match
    for name in EU_27_NAMES:
        if name in loc_lower:
            return True, loc
    # Bare ISO-2 code
    if loc_lower.strip() in EU_27_CODES:
        return True, loc
    # City-name fallback: check each word/phrase in location against known EU cities
    for city, country in EU_CITY_MAP.items():
        if city in loc_lower:
            return True, f"{loc} (resolved: {country})"
    return False, loc


def tier2_signals(owner, repo, homepage):
    signals = {'gdpr': False, 'eu_lang': False, 'eu_cloud': False, 'eu_domain': False}

    # README — signals (a), (b), (d-partial)
    for name in ['README.md', 'README.rst', 'README.txt', 'README']:
        text = file_content(owner, repo, name)
        if text:
            signals['gdpr'] = bool(GDPR_RE.search(text))
            try:
                lang = detect(text)
                signals['eu_lang'] = lang in EU_OFFICIAL_LANGS
            except LangDetectException:
                pass
            if EU_DOMAIN_RE.search(text):
                signals['eu_domain'] = True
            break

    # Homepage URL — signal (d-partial)
    if homepage and EU_DOMAIN_RE.search(homepage):
        signals['eu_domain'] = True

    # CI workflows — signal (c)
    workflows = gh(f'repos/{owner}/{repo}/contents/.github/workflows')
    if workflows and isinstance(workflows, list):
        for wf in workflows[:5]:
            wf_text = file_content(owner, repo, wf.get('path', ''))
            if wf_text and EU_CLOUD_RE.search(wf_text):
                signals['eu_cloud'] = True
                break

    count = sum(signals.values())
    return signals, count


def fetch_repos(n=20):
    seen, repos = set(), []
    page = 1
    while len(repos) < n and page <= 5:
        cmd = [
            'gh', 'api', 'search/code',
            '-X', 'GET',
            '-f', 'q=filename:copilot-instructions.md path:.github',
            '-f', f'per_page=30',
            '-f', f'page={page}',
            '--jq', '.items[] | {repo: .repository.full_name, owner: .repository.owner.login, homepage: .repository.homepage}'
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        for line in r.stdout.strip().split('\n'):
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item['repo'] not in seen:
                seen.add(item['repo'])
                repos.append(item)
                if len(repos) >= n:
                    break
        page += 1
        time.sleep(2)
    return repos[:n]


def main():
    print("Fetching 20 Copilot-configured repos...")
    repos = fetch_repos(20)
    print(f"Got {len(repos)} unique repos\n")

    results = []
    for i, r in enumerate(repos):
        owner = r['owner']
        repo_name = r['repo'].split('/')[-1]
        homepage = r.get('homepage') or ''
        print(f"[{i+1:02d}/20] {r['repo']}")

        is_t1, loc = tier1(owner)
        time.sleep(0.5)

        if is_t1:
            tier = 'Tier 1'
            sigs = {}
            sig_count = 0
            print(f"        Tier 1 — EU-established ({loc})")
        else:
            sigs, sig_count = tier2_signals(owner, repo_name, homepage)
            tier = 'Tier 2' if sig_count >= 2 else 'Out of scope'
            print(f"        {tier} — location={loc!r} signals={sig_count}/4 "
                  f"gdpr={sigs['gdpr']} lang={sigs['eu_lang']} "
                  f"cloud={sigs['eu_cloud']} domain={sigs['eu_domain']}")
        time.sleep(0.5)

        results.append({
            'repo': r['repo'],
            'location': loc,
            'tier': tier,
            'gdpr': sigs.get('gdpr', '—'),
            'eu_lang': sigs.get('eu_lang', '—'),
            'eu_cloud': sigs.get('eu_cloud', '—'),
            'eu_domain': sigs.get('eu_domain', '—'),
            'signals': sig_count,
        })

    t1 = [x for x in results if x['tier'] == 'Tier 1']
    t2 = [x for x in results if x['tier'] == 'Tier 2']
    oos = [x for x in results if x['tier'] == 'Out of scope']

    print(f"\n{'='*65}")
    print(f"JURISDICTIONAL SCOPING SUMMARY (n={len(results)})")
    print(f"{'='*65}")
    print(f"  Tier 1  (EU-established, direct obligation):    {len(t1):>3}")
    print(f"  Tier 2  (non-EU, extraterritorial scope):       {len(t2):>3}")
    print(f"  Out of scope (no demonstrable EU nexus):        {len(oos):>3}")
    print(f"  In-scope total:                                 {len(t1)+len(t2):>3} "
          f"({100*(len(t1)+len(t2))/len(results):.1f}%)")

    print(f"\n{'Repo':<45} {'Tier':<12} {'Location'}")
    print('-' * 80)
    for x in results:
        print(f"  {x['repo']:<43} {x['tier']:<12} {x['location'] or '(none)'}")

    # Save for paper
    with open('/Users/apple/pr-automation-agent/tmp/jurisdiction_results.json', 'w') as f:
        json.dump({'summary': {
            'total': len(results),
            'tier1': len(t1),
            'tier2': len(t2),
            'out_of_scope': len(oos),
            'in_scope': len(t1) + len(t2),
        }, 'repos': results}, f, indent=2)
    print("\nResults saved to tmp/jurisdiction_results.json")


if __name__ == '__main__':
    main()
