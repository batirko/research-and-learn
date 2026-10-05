/* The portal's main script: read marks, filters, the theme switch, the context
 * toggle, the open-all control for private blocks, search, the glossary's term
 * finder and print. Every page works without it.
 *
 * Storage is optional and wrapped: a page opened from disk might not get it.
 * window.GUIDE, set in each page's head, holds the storage key prefix. The search
 * index is data in search-index.js, which only the search page loads. */
(function () {
  'use strict';

  var config = window.GUIDE || {};
  var prefix = config.key || 'guide';
  var KEY_READ = prefix + '-read';
  var KEY_THEME = prefix + '-theme';
  var KEY_CONTEXT = prefix + '-hide-context';
  var root = document.documentElement;

  function load(key) { try { return window.localStorage.getItem(key); } catch (e) { return null; } }
  function save(key, value) { try { window.localStorage.setItem(key, value); } catch (e) { /* no storage */ } }
  function each(sel, fn, scope) { Array.prototype.forEach.call((scope || document).querySelectorAll(sel), fn); }

  /* ---------- read marks ---------- */
  /* notes.js keeps them in its store. Without it, a list in this browser's storage holds them. */
  var notes = window.GuideNotes;
  var read = {};
  try { (JSON.parse(load(KEY_READ) || '[]') || []).forEach(function (id) { read[id] = true; }); } catch (e) { read = {}; }
  function isRead(id) { return notes ? notes.isRead(id) : !!read[id]; }
  function setRead(id, on) {
    if (notes) { notes.setRead(id, on); return; }
    if (on) { read[id] = true; } else { delete read[id]; }
    save(KEY_READ, JSON.stringify(Object.keys(read)));
  }

  function paintRead() {
    each('[data-topic-id]', function (el) {
      el.classList.toggle('is-read', isRead(el.getAttribute('data-topic-id')));
    });
    each('[data-read-toggle]', function (b) {
      var on = isRead(b.getAttribute('data-id'));
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.textContent = on ? 'Read ✓' : 'Mark as read';
    });
    var p = document.querySelector('[data-progress]');
    if (p) {
      var ids = (p.getAttribute('data-written') || '').split(' ').filter(Boolean);
      var n = ids.filter(isRead).length;
      p.textContent = n ? 'You have read ' + n + ' of them.' : '';
    }
  }

  /* ---------- filters ---------- */
  function applyFilters(box) {
    var ranks = [], writtenOnly = false;
    each('[data-filter][aria-pressed="true"]', function (b) {
      if (b.getAttribute('data-filter') === 'rank') { ranks.push(b.getAttribute('data-value')); }
      if (b.getAttribute('data-filter') === 'status') { writtenOnly = true; }
    }, box);
    each('[data-rank][data-status]', function (row) {
      var out = (ranks.length && ranks.indexOf(row.getAttribute('data-rank')) < 0) ||
                (writtenOnly && row.getAttribute('data-status') !== 'written');
      row.classList.toggle('is-filtered-out', !!out);
    }, box);
    each('[data-filter-group]', function (g) {
      var visible = g.querySelectorAll('[data-rank][data-status]:not(.is-filtered-out)').length;
      g.classList.toggle('is-empty', visible === 0);
    }, box);
    var reset = box.querySelector('[data-filter-reset]');
    if (reset) { reset.hidden = !(ranks.length || writtenOnly); }
  }

  /* ---------- theme ---------- */
  function currentTheme() { return root.getAttribute('data-theme') || 'auto'; }
  function paintTheme() {
    each('[data-theme-toggle]', function (b) { b.textContent = 'Theme: ' + currentTheme(); });
  }

  /* ---------- context sections ---------- */
  function paintContext() {
    var on = root.classList.contains('hide-context');
    each('[data-context-toggle]', function (b) {
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.textContent = on ? 'Show context sections' : 'Hide context sections';
    });
  }

  /* ---------- private blocks: open all, close all ---------- */
  /* Not remembered on purpose: every page opens with its private facts closed. */
  function privateBlocks() { return Array.prototype.slice.call(document.querySelectorAll('details.private')); }
  function allPrivateOpen() {
    var all = privateBlocks();
    return all.length > 0 && all.every(function (d) { return d.open; });
  }
  function paintPrivate() {
    var on = allPrivateOpen();
    each('[data-private-toggle]', function (b) {
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.textContent = on ? 'Close all private facts' : 'Open all private facts';
    });
  }
  document.addEventListener('toggle', function (e) {
    if (e.target.classList && e.target.classList.contains('private')) { paintPrivate(); }
  }, true);

  /* ---------- search ---------- */
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }
  function reEsc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  var RANK_LABELS = config.ranks || { critical: 'Critical', high: 'High', medium: 'Medium', context: 'Context' };
  function chip(rank) { return RANK_LABELS[rank] ? '<span class="rank rank-' + rank + '">' + esc(RANK_LABELS[rank]) + '</span>' : ''; }

  function initSearch() {
    var input = document.querySelector('[data-search-input]');
    var out = document.querySelector('[data-search-results]');
    var status = document.querySelector('[data-search-status]');
    if (!input || !out) { return; }
    var data = window.GUIDE_SEARCH;
    if (!data) { status.textContent = 'The search index is missing. Run the build again.'; return; }
    var ids = Object.keys(data.topics);
    var rows = [];
    /* One row per page matches its title alone; the other rows are its parts and sections. */
    ids.forEach(function (id) { rows.push({ id: id, anchor: '', title: '', rank: '', text: '', titleRow: true }); });
    data.entries.forEach(function (e) {
      rows.push({ id: e[0], anchor: e[1], title: e[2], rank: e[3], text: e[4] });
    });

    function terms(q) {
      var list = [], m, re = /"([^"]+)"|(\S+)/g;
      while ((m = re.exec(q))) {
        var w = (m[1] || m[2]).trim();
        if (w.length > 1) { list.push(new RegExp((/^\w/.test(w) ? '\\b' : '') + reEsc(w), 'gi')); }
      }
      return list;
    }
    function count(re, s) { re.lastIndex = 0; var n = 0; while (re.exec(s) && n < 20) { n++; } return n; }
    function snippet(text, list) {
      var at = -1;
      list.forEach(function (re) { re.lastIndex = 0; var m = re.exec(text); if (m && (at < 0 || m.index < at)) { at = m.index; } });
      if (at < 0) { return ''; }
      var start = Math.max(0, at - 70), end = Math.min(text.length, at + 190);
      if (start > 0) { start = text.indexOf(' ', start) + 1; }
      if (end < text.length) { end = text.lastIndexOf(' ', end); }
      var piece = text.slice(start, end);
      var all = new RegExp(list.map(function (re) { return re.source; }).join('|'), 'gi');
      var out = '', last = 0, m;
      while ((m = all.exec(piece))) {
        if (!m[0]) { all.lastIndex++; continue; }
        out += esc(piece.slice(last, m.index)) + '<mark>' + esc(m[0]) + '</mark>';
        last = m.index + m[0].length;
      }
      out += esc(piece.slice(last));
      return (start > 0 ? '… ' : '') + out + (end < text.length ? ' …' : '');
    }

    function run() {
      var q = input.value.trim();
      var list = terms(q);
      if (!list.length) { out.innerHTML = ''; status.textContent = q ? 'Type at least two letters.' : ''; return; }
      var byPage = {}, nHits = 0;
      rows.forEach(function (r) {
        var t = data.topics[r.id];
        var score = 0, own = 0;
        for (var i = 0; i < list.length; i++) {
          var inText = count(list[i], r.text), inTitle = count(list[i], r.title), inPage = count(list[i], t[0]);
          if (r.titleRow ? !inPage : !(inText || inTitle || inPage)) { return; }
          own += inText + inTitle;
          score += r.titleRow ? 10 * inPage : inText + 8 * inTitle + 2 * inPage;
        }
        if (!r.titleRow && !own) { return; }
        (byPage[r.id] = byPage[r.id] || []).push({ r: r, score: score });
        if (!r.titleRow) { nHits++; }
      });
      var found = Object.keys(byPage).map(function (id) {
        var all = byPage[id].sort(function (a, b) { return b.score - a.score; });
        var hits = all.filter(function (h) { return !h.r.titleRow; });
        return { id: id, hits: hits, score: all[0].score + hits.length };
      }).sort(function (a, b) { return b.score - a.score || ids.indexOf(a.id) - ids.indexOf(b.id); });
      if (!found.length) {
        status.textContent = 'Nothing matches ' + q + '.';
        out.innerHTML = '';
        return;
      }
      status.textContent = found.length + (found.length === 1 ? ' page matches ' : ' pages match ') + q +
        (nHits ? ', in ' + nHits + (nHits === 1 ? ' place.' : ' places.') : '.');
      out.innerHTML = found.map(function (f) {
        var t = data.topics[f.id];
        var idSpan = t[4] ? '<span class="topic-id">' + esc(f.id) + '</span> ' : '';
        var head = '<h2 class="hit-topic"><a href="' + esc(t[1]) + '">' + idSpan + esc(t[0]) + '</a> ' + chip(t[2]) + '</h2>';
        if (!t[3]) { return '<section class="hit-group">' + head + '<p class="hit-planned"><span class="status status-planned">Planned</span> Its page shows the plan from the topic map.</p></section>'; }
        if (!f.hits.length) { return '<section class="hit-group">' + head + '</section>'; }
        var shown = f.hits.slice(0, 6).map(function (h) {
          return '<li class="hit"><p class="hit-head"><a href="' + esc(t[1] + '#' + h.r.anchor) + '">' + esc(h.r.title) + '</a> ' + chip(h.r.rank) + '</p>' +
                 '<p class="hit-snip">' + snippet(h.r.text, list) + '</p></li>';
        }).join('');
        var more = f.hits.length > 6 ? '<p class="hit-more">And ' + (f.hits.length - 6) + ' more on this page.</p>' : '';
        return '<section class="hit-group">' + head + '<ol class="hits">' + shown + '</ol>' + more + '</section>';
      }).join('');
    }

    var timer = null;
    input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(run, 120); });
    var form = input.closest('form');
    if (form) { form.addEventListener('submit', function (e) { e.preventDefault(); run(); }); }
    var q = null;
    try { q = new URLSearchParams(window.location.search).get('q'); } catch (e) { q = null; }
    if (q && !input.value) { input.value = q; }
    if (input.value) { run(); }
    input.focus();
  }

  /* ---------- glossary: find a term ---------- */
  /* It matches each row's public words only: data-gl-text never holds what a private block holds. */
  function initGlossary() {
    var box = document.querySelector('[data-gl-find]');
    if (!box) { return; }
    var input = box.querySelector('[data-gl-input]');
    var status = box.querySelector('[data-gl-status]');
    var rows = Array.prototype.slice.call(document.querySelectorAll('.gl-row'));
    var secs = Array.prototype.slice.call(document.querySelectorAll('[data-gl-sec]'));
    box.hidden = false;
    input.addEventListener('input', function () {
      var words = input.value.toLowerCase().split(/\s+/).filter(Boolean);
      var shown = 0;
      rows.forEach(function (r) {
        var text = r.getAttribute('data-gl-text') || '';
        var hit = words.every(function (w) { return text.indexOf(w) >= 0; });
        r.classList.toggle('is-filtered-out', !hit);
        if (hit) { shown++; }
      });
      secs.forEach(function (s) { s.classList.toggle('is-empty', !s.querySelector('.gl-row:not(.is-filtered-out)')); });
      status.textContent = words.length ? (shown ? shown + ' of ' + rows.length + ' terms match.' : 'No term matches. Try a shorter word.') : '';
    });
  }

  /* ---------- print ---------- */
  /* A page prints what you see. A closed private block prints its title only. The job
   * statements of visuals open for paper and close again after. */
  var openedForPrint = [];
  window.addEventListener('beforeprint', function () {
    openedForPrint = Array.prototype.filter.call(document.querySelectorAll('details.visual-job:not([open])'), function (d) {
      d.open = true; return true;
    });
    var all = privateBlocks();
    var closed = all.filter(function (d) { return !d.open; }).length;
    var text = '';
    if (all.length && closed === all.length) {
      text = 'This copy leaves out all ' + all.length + ' private blocks: each prints its title only. To print one, open it first.';
    } else if (closed) {
      text = 'This copy leaves out ' + closed + ' of ' + all.length + ' private blocks. It holds the ' + (all.length - closed) +
             ' you opened, with private facts. Keep it to yourself.';
    } else if (all.length) {
      text = 'This copy holds all ' + all.length + ' private blocks, with private facts. Keep it to yourself.';
    }
    each('[data-print-note]', function (p) {
      if (!p.hasAttribute('data-default')) { p.setAttribute('data-default', p.textContent); }
      p.textContent = text || p.getAttribute('data-default');
    });
  });
  window.addEventListener('afterprint', function () {
    openedForPrint.forEach(function (d) { d.open = false; });
    openedForPrint = [];
  });

  document.addEventListener('click', function (e) {
    var t = e.target.closest ? e.target : e.target.parentElement;
    if (!t) { return; }
    var b;
    if ((b = t.closest('[data-read-toggle]'))) {
      var id = b.getAttribute('data-id');
      setRead(id, !isRead(id));
      paintRead();
    } else if ((b = t.closest('[data-filter]'))) {
      b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      applyFilters(b.closest('[data-filterable]'));
    } else if ((b = t.closest('[data-filter-reset]'))) {
      var box = b.closest('[data-filterable]');
      each('[data-filter]', function (f) { f.setAttribute('aria-pressed', 'false'); }, box);
      applyFilters(box);
    } else if ((b = t.closest('[data-theme-toggle]'))) {
      var next = { auto: 'light', light: 'dark', dark: 'auto' }[currentTheme()];
      if (next === 'auto') { root.removeAttribute('data-theme'); } else { root.setAttribute('data-theme', next); }
      save(KEY_THEME, next);
      paintTheme();
    } else if ((b = t.closest('[data-private-toggle]'))) {
      var open = !allPrivateOpen();
      privateBlocks().forEach(function (d) { d.open = open; });
      paintPrivate();
    } else if ((b = t.closest('[data-context-toggle]'))) {
      root.classList.toggle('hide-context');
      save(KEY_CONTEXT, root.classList.contains('hide-context') ? '1' : '0');
      paintContext();
    }
  });

  if (notes) { notes.onChange(paintRead); }
  paintRead();
  paintTheme();
  paintContext();
  paintPrivate();
  initSearch();
  initGlossary();
})();
