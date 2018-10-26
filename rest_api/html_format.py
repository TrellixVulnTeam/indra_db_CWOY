"""
Format a set of INDRA Statements into an HTML-based format.
"""
import sys
import csv
from os.path import abspath, dirname, join
import re
import json
from collections import defaultdict
from jinja2 import Template
from indra.sources import indra_db_rest
from indra.assemblers.english import EnglishAssembler
from indra.statements import stmts_from_json
from indra.databases import get_identifiers_url

# Create a template object from the template file, load once
template_path = join(dirname(abspath(__file__)), 'template.html')
with open(template_path, 'rt') as f:
    template_str = f.read()
    template = Template(template_str)

# TODO:
# - Highlight text in english assembled sentences
# - Highlight text in evidence sentences
# - For both, add links to identifiers.org



def format_evidence_text(stmt, stmt_hash):
    """Highlight subject and object in raw text strings."""
    ev_list = []
    for ix, ev in enumerate(stmt.evidence):
        if ev.text is None:
            format_text = '(None available)'
        else:
            format_text = ev.text
        """
            indices = {}
            for ix, ag in enumerate(stmt.agent_list()):
                ag_text = ev.annotations['agents']['raw_text'][ix]
                if ag_text is None:
                    continue
                marker = '<span class="label label-primary">'
                indices[ag_text] = [(m.start(), m.start() + len(ag_text))
                                    for m in re.finditer(ag_text, ev.text)]
                indices 
                n = len(ag_text)
                last = 0
                for s in starts:
                    in
                    ag_start_ix = format_text.find(ag_text)
                    ag_end_ix = ag_start_ix + len(ag_text)
                    format_text = (format_text[0:ag_start_ix] + marker +
                                  format_text[ag_start_ix:ag_end_ix] + '</span>' +
                                   format_text[ag_end_ix:])
        """
        """
        ag_name_list = [(ix, ag.name) for ix, ag in enumerate(agent_list)]
        #subj_ag_index = ag_name_list.index(edge[0])
        #obj_ag_index = ag_name_list.index(edge[1])
        #subj_text = evidence.annotations['agents']['raw_text'][subj_ag_index]
        #obj_text = evidence.annotations['agents']['raw_text'][obj_ag_index]
        # TODO: highlight all instances of each gene, not just the first
        format_text = raw_text
        for ix, ag_text in enumerate((subj_text, obj_text)):
            if ag_text is None:
                continue
            if ix == 0:
                marker = '<span class="label label-primary">'
            else:
                marker = '<span class="label label-primary">'
            ag_start_ix = format_text.find(ag_text)
            ag_end_ix = ag_start_ix + len(ag_text)
            format_text = (format_text[0:ag_start_ix] + marker +
                           format_text[ag_start_ix:ag_end_ix] + '</span>' +
                           format_text[ag_end_ix:])
        return format_text
        """
        evidence_id = f"{stmt_hash}-{ix}"
        ev_list.append({'source_api': ev.source_api,
                        'pmid': ev.pmid, 'text': format_text,
                        'evidence_id': evidence_id})
    return ev_list


def format_statements(result):
    #stmt_json = result.pop('statements')
    #stmt_str = json.dumps(stmt_json) if stmt_json else "No statements."

    """
    for subj, obj in edges:
        for stmt in stmts:
            for ev in stmt.evidence:
                #content[stmt][(subj, obj)].append(stmt.evidence)
                content[(subj, obj)].append({
                  'source_api': ev.source_api,
                  'pmid': ev.pmid,
                  'text': format_evidence_text((subj, obj), stmt.agent_list(), ev)
               })
    """
    stmts_formatted = []
    # Each entry in the statement list will have
    # - English assembled top level
    # - (optional INDRA Statement raw)
    # - HTML formatted evidence (with clickable entity names?)

    stmts_json = result.pop('statements')
    for stmt_hash, stmt_json in stmts_json.items():
        stmt = stmts_from_json([stmt_json])[0] # TODO: Need to go back to stmt?
        ea = EnglishAssembler([stmt])
        english = ea.make_model()
        ev_list = format_evidence_text(stmt, stmt_hash)
        total_evidence = result['evidence_totals'][int(stmt_hash)]
        stmts_formatted.append({
            'hash': stmt_hash,
            'english': english,
            'evidence': ev_list,
            'evidence_returned': len(ev_list),
            'total_evidence': total_evidence})
    return template.render(statements=stmts_formatted, **result)
    #return f"<pre>{json.dumps(result['statements'], indent=4)}</pre>"
