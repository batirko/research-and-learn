/* Bookmarks, notes, to-dos and read marks, kept in this browser's storage.
 *
 * Nothing leaves the browser. Every page works without storage: the notes
 * layer just has nothing to show. The notes page can download a copy as a
 * file and load one back, which is how notes move to another browser.
 *
 * A note on a sentence stores the sentence, a few words on each side, and the
 * id of the section it sits in. After a rebuild, the script finds the sentence
 * again by its text. When the text has changed, the note stays on the notes
 * page with a flag. */
(function () {
  'use strict';

  var config = window.GUIDE || {};
  var prefix = config.key || 'guide';
  var KEY_STORE = prefix + '-notes';
  var KEY_READ_LIST = prefix + '-read';   // read marks kept by site.js when this script is absent
  var CONTEXT = 48;
  var lang = document.documentElement.lang || undefined;

  var storageWorks = true;
  function load(k) { try { return window.localStorage.getItem(k); } catch (e) { storageWorks = false; return null; } }
  function keep(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { storageWorks = false; } }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }
  function each(sel, fn, scope) { Array.prototype.forEach.call((scope || document).querySelectorAll(sel), fn); }

  var pageKey = (window.location.pathname.split('/').pop() || '').replace(/\.html$/, '') || 'index';
  var suffix = config.title ? ' · ' + config.title : '';
  var pageTitle = suffix && document.title.slice(-suffix.length) === suffix ? document.title.slice(0, -suffix.length) : document.title;
  var main = document.getElementById('main');
  var annotatable = !!main && pageKey !== 'notes' && pageKey !== 'search';

  /* ---------------------------------------------------------------- store */

  var store = { items: {}, lost: {} };
  try {
    var saved = JSON.parse(load(KEY_STORE) || 'null');
    if (saved && saved.items) { store = { items: saved.items, lost: saved.lost || {}, readImported: saved.readImported }; }
  } catch (e) { /* start empty */ }

  function persist() { keep(KEY_STORE, JSON.stringify(store)); }

  // Read marks that site.js kept on its own join the store once.
  if (!store.readImported) {
    try {
      (JSON.parse(load(KEY_READ_LIST) || '[]') || []).forEach(function (id) {
        var key = 'read-' + id;
        if (!store.items[key]) {
          store.items[key] = { id: key, updated: 1, deleted: 0, data: { kind: 'read', page: String(id).toLowerCase() } };
        }
      });
    } catch (e) { /* nothing to import */ }
    store.readImported = true;
    persist();
  }

  function newId() { return 'n-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8); }

  function put(id, data, deleted) {
    var prev = store.items[id];
    var t = Date.now();
    if (prev && prev.updated >= t) { t = prev.updated + 1; }
    store.items[id] = { id: id, updated: t, deleted: deleted ? 1 : 0, data: data };
    persist();
    changed();
  }

  function marks() {
    return Object.keys(store.items).map(function (k) { return store.items[k]; })
      .filter(function (it) { return !it.deleted && it.data && it.data.kind === 'mark'; });
  }

  function kindOf(d) { return d.todo ? 'todo' : (d.body ? 'note' : 'bookmark'); }
  var KIND_LABEL = { bookmark: 'Bookmark', note: 'Note', todo: 'To-do' };

  var listeners = [];
  function changed() {
    paintPage();
    renderNotesPage();
    paintState();
    listeners.forEach(function (fn) { try { fn(); } catch (e) { /* a listener's problem */ } });
  }

  function stateText() {
    if (!storageWorks) {
      return 'This browser doesn’t let the page store anything, so what you save here lasts only until you leave the page.';
    }
    var n = marks().length;
    var what = n === 1 ? '1 item' : n + ' items';
    return what + ' saved in this browser only. Clearing the browser’s site data deletes them, so download a copy to keep one.';
  }
  function paintState() { each('[data-notes-state]', function (p) { p.textContent = stateText(); }); }

  /* ---------------------------------------------------------------- finding text */

  var SKIP = 'svg, script, style, textarea, input, button, select, [data-notes-ui]';

  // The text of a scope with each run of white space collapsed to one space, and for every
  // character the text node and offset it came from.
  function textMap(scope) {
    var walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) { return n.parentElement && n.parentElement.closest(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT; }
    });
    var nodes = [], ni = [], off = [], parts = [], space = true, n;
    while ((n = walker.nextNode())) {
      var k = nodes.length, d = n.data;
      nodes.push(n);
      for (var i = 0; i < d.length; i++) {
        var c = d.charAt(i);
        if (/\s/.test(c)) {
          if (space) { continue; }
          c = ' ';
          space = true;
        } else {
          space = false;
        }
        parts.push(c); ni.push(k); off.push(i);
      }
    }
    return { nodes: nodes, ni: ni, off: off, text: parts.join('') };
  }

  function pointIndex(m, container, offset) {
    var k = m.nodes.indexOf(container);
    if (k < 0) {
      var r = document.createRange();
      r.setStart(container, offset);
      r.collapse(true);
      for (var j = 0; j < m.nodes.length; j++) {
        if (r.comparePoint(m.nodes[j], 0) >= 0) { k = j; break; }
      }
      if (k < 0) { return m.text.length; }
      offset = 0;
    }
    for (var i = 0; i < m.ni.length; i++) {
      if (m.ni[i] > k || (m.ni[i] === k && m.off[i] >= offset)) { return i; }
    }
    return m.text.length;
  }

  function headingOf(section) {
    if (!section) { return ''; }
    var h = section.querySelector('h1, h2, h3, h4');
    if (!h) { return ''; }
    var copy = h.cloneNode(true);
    each('[data-notes-ui]', function (x) { x.parentNode.removeChild(x); }, copy);
    return copy.textContent.replace(/\s+/g, ' ').trim();
  }

  function describe(range) {
    var from = range.commonAncestorContainer;
    var el = from.nodeType === 1 ? from : from.parentElement;
    var section = el && el.closest('section[id]');
    if (section && !main.contains(section)) { section = null; }
    var m = textMap(section || main);
    var s = pointIndex(m, range.startContainer, range.startOffset);
    var e = pointIndex(m, range.endContainer, range.endOffset);
    while (s < e && m.text.charAt(s) === ' ') { s++; }
    while (e > s && m.text.charAt(e - 1) === ' ') { e--; }
    // A selection that stops inside a word takes the whole word.
    var word = /[\wÀ-ɏ'’-]/;
    while (s > 0 && s < e && word.test(m.text.charAt(s - 1)) && word.test(m.text.charAt(s))) { s--; }
    while (e < m.text.length && e > s && word.test(m.text.charAt(e)) && word.test(m.text.charAt(e - 1))) { e++; }
    if (e - s < 2) { return null; }
    return {
      anchor: section ? section.id : '', section: headingOf(section),
      quote: m.text.slice(s, e).slice(0, 4000),
      prefix: m.text.slice(Math.max(0, s - CONTEXT), s), suffix: m.text.slice(e, e + CONTEXT)
    };
  }

  function sharedEnd(a, b) { var n = 0; while (n < a.length && n < b.length && a.charAt(a.length - 1 - n) === b.charAt(b.length - 1 - n)) { n++; } return n; }
  function sharedStart(a, b) { var n = 0; while (n < a.length && n < b.length && a.charAt(n) === b.charAt(n)) { n++; } return n; }

  // The saved sentence's best match on the page: the occurrence whose surroundings share the most text.
  function locate(d) {
    var section = d.anchor ? document.getElementById(d.anchor) : null;
    var scopes = section ? [section, main] : [main];
    for (var i = 0; i < scopes.length; i++) {
      var m = textMap(scopes[i]), best = -1, bestScore = -1, at = m.text.indexOf(d.quote);
      while (at >= 0) {
        var score = sharedEnd(m.text.slice(Math.max(0, at - CONTEXT), at), d.prefix || '') +
                    sharedStart(m.text.slice(at + d.quote.length, at + d.quote.length + CONTEXT), d.suffix || '');
        if (score > bestScore) { best = at; bestScore = score; }
        at = m.text.indexOf(d.quote, at + 1);
      }
      if (best >= 0) { return { m: m, s: best, e: best + d.quote.length }; }
    }
    return null;
  }

  function wrap(hit, item) {
    var m = hit.m, first = null, startK = m.ni[hit.s], endK = m.ni[hit.e - 1];
    for (var k = startK; k <= endK; k++) {
      var node = m.nodes[k];
      var a = k === startK ? m.off[hit.s] : 0;
      var b = k === endK ? m.off[hit.e - 1] + 1 : node.data.length;
      if (!node.data.slice(a, b).trim()) { continue; }
      var target = a > 0 ? node.splitText(a) : node;
      if (b - a < target.data.length) { target.splitText(b - a); }
      var mark = document.createElement('mark');
      mark.className = 'ann ann-' + kindOf(item.data) + (item.data.done ? ' is-done' : '');
      mark.setAttribute('data-ann', item.id);
      target.parentNode.insertBefore(mark, target);
      mark.appendChild(target);
      if (!first) { first = mark; }
    }
    return first;
  }

  function clearPage() {
    each('mark.ann', function (mk) {
      var parent = mk.parentNode;
      while (mk.firstChild) { parent.insertBefore(mk.firstChild, mk); }
      parent.removeChild(mk);
      parent.normalize();
    });
    each('.ann-pill', function (p) { p.parentNode.removeChild(p); });
  }

  /* ---------------------------------------------------------------- the page */

  function headingFor(anchor) {
    var section = anchor ? document.getElementById(anchor) : null;
    if (anchor && !section) { return null; }
    if (!section) { return main.querySelector('h1'); }
    return section.querySelector('h1, h2, h3, h4');
  }

  function paintPage() {
    if (!annotatable) { return; }
    clearPage();
    var bySection = {}, lostChanged = false;
    marks().filter(function (it) { return it.data.page === pageKey; }).forEach(function (it) {
      var d = it.data, lost = false;
      if (d.quote) {
        var hit = locate(d);
        if (hit) { var first = wrap(hit, it); if (first) { first.id = 'ann-' + it.id; } } else { lost = true; }
      } else if (headingFor(d.anchor || '')) {
        (bySection[d.anchor || ''] = bySection[d.anchor || ''] || []).push(it);
      } else {
        lost = true;
      }
      if (!!store.lost[it.id] !== lost) {
        if (lost) { store.lost[it.id] = true; } else { delete store.lost[it.id]; }
        lostChanged = true;
      }
    });
    if (lostChanged) { persist(); }
    Object.keys(bySection).forEach(function (anchor) {
      var list = bySection[anchor], h = headingFor(anchor);
      var label = list.length === 1 ? ({ bookmark: 'Bookmarked', note: 'Note', todo: list[0].data.done ? 'To-do done' : 'To-do' })[kindOf(list[0].data)]
                                    : list.length + ' saved';
      var pill = document.createElement('button');
      pill.type = 'button';
      pill.className = 'ann-pill';
      pill.setAttribute('data-notes-ui', '');
      pill.setAttribute('data-ann-section', anchor);
      pill.textContent = label;
      h.appendChild(pill);
    });
  }

  function addHeadingButtons() {
    if (!annotatable) { return; }
    var heads = [];
    var h1 = main.querySelector('h1');
    if (h1) { heads.push([h1, '']); }
    each('section[id]', function (s) {
      var h = s.querySelector('h2, h3, h4');
      if (h && h.closest('section[id]') === s) { heads.push([h, s.id]); }
    }, main);
    heads.forEach(function (pair) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'ann-add';
      b.setAttribute('data-notes-ui', '');
      b.setAttribute('data-ann-section', pair[1]);
      b.setAttribute('aria-label', pair[1] ? 'Save this section' : 'Save this page');
      b.title = pair[1] ? 'Bookmark this section, or add a note or to-do' : 'Bookmark this page, or add a note or to-do';
      pair[0].appendChild(b);
    });
  }

  function revealHash() {
    var id = decodeURIComponent(window.location.hash.slice(1));
    if (!/^ann-/.test(id)) { return; }
    var el = document.getElementById(id);
    if (!el) { return; }
    var d = el.closest('details');
    while (d) { d.open = true; d = d.parentElement && d.parentElement.closest('details'); }
    el.scrollIntoView({ block: 'center' });
    each('mark[data-ann="' + id.slice(4) + '"]', function (mk) {
      mk.classList.add('is-flash');
      setTimeout(function () { mk.classList.remove('is-flash'); }, 2000);
    });
  }

  /* ---------------------------------------------------------------- the selection bar */

  var ui = document.createElement('div');
  ui.setAttribute('data-notes-ui', '');
  ui.innerHTML =
    '<div class="ann-bar" role="toolbar" aria-label="Save the selected text" hidden>' +
      '<button type="button" data-ann-act="bookmark">Bookmark</button>' +
      '<button type="button" data-ann-act="note">Note</button>' +
      '<button type="button" data-ann-act="todo">To-do</button></div>' +
    '<p class="ann-toast" role="status" hidden><span data-toast-text></span> <button type="button" data-toast-undo hidden>Undo</button></p>' +
    '<dialog class="ann-sheet" aria-labelledby="ann-sheet-title">' +
      '<form method="dialog" class="ann-form">' +
        '<h2 class="ann-sheet-title" id="ann-sheet-title"></h2>' +
        '<p class="ann-where"></p>' +
        '<blockquote class="ann-quote" hidden></blockquote>' +
        '<ul class="ann-existing" hidden></ul>' +
        '<label class="ann-label" for="ann-body">Note</label>' +
        '<textarea id="ann-body" rows="4" placeholder="Leave it empty to keep a bookmark"></textarea>' +
        '<p class="ann-checks"><label><input type="checkbox" id="ann-todo"> To-do</label>' +
        '<label id="ann-done-wrap"><input type="checkbox" id="ann-done"> Done</label></p>' +
        '<p class="ann-buttons"><button type="submit" value="save" class="ann-primary">Save</button>' +
        '<button type="submit" value="cancel">Cancel</button>' +
        '<button type="submit" value="delete" class="ann-danger">Delete</button></p>' +
      '</form></dialog>';
  document.body.appendChild(ui);

  var bar = ui.querySelector('.ann-bar');
  var toast = ui.querySelector('.ann-toast');
  var sheet = ui.querySelector('.ann-sheet');
  var selected = null, hideTimer = null;

  function onSelection() {
    if (!annotatable) { return; }
    var sel = window.getSelection();
    var range = sel && sel.rangeCount ? sel.getRangeAt(0) : null;
    var inside = range && !sel.isCollapsed && main.contains(range.commonAncestorContainer) &&
                 !(range.commonAncestorContainer.nodeType === 1 && range.commonAncestorContainer.closest('[data-notes-ui]'));
    if (inside) {
      var d = describe(range);
      if (d) { selected = d; clearTimeout(hideTimer); bar.hidden = false; return; }
    }
    // A tap on the bar can clear the selection before the click arrives, so the bar waits a moment.
    clearTimeout(hideTimer);
    hideTimer = setTimeout(function () { bar.hidden = true; selected = null; }, 400);
  }
  var selTimer = null;
  document.addEventListener('selectionchange', function () { clearTimeout(selTimer); selTimer = setTimeout(onSelection, 120); });
  bar.addEventListener('mousedown', function (e) { e.preventDefault(); });

  bar.addEventListener('click', function (e) {
    var b = e.target.closest('[data-ann-act]');
    if (!b || !selected) { return; }
    var act = b.getAttribute('data-ann-act'), target = selected;
    bar.hidden = true;
    selected = null;
    try { window.getSelection().removeAllRanges(); } catch (err) { /* nothing selected */ }
    if (act === 'bookmark') {
      put(newId(), fresh(target, '', false), false);
      say('Bookmarked. Tap the highlight to add a note.');
    } else {
      openSheet({ target: target, todo: act === 'todo' });
    }
  });

  function fresh(target, body, todo) {
    return {
      kind: 'mark', page: pageKey, pageTitle: pageTitle,
      anchor: target.anchor || '', section: target.section || '',
      quote: target.quote || '', prefix: target.prefix || '', suffix: target.suffix || '',
      body: body, todo: !!todo, done: false, created: Date.now()
    };
  }

  var toastTimer = null, undoFn = null;
  function say(text, undo) {
    toast.querySelector('[data-toast-text]').textContent = text;
    var u = toast.querySelector('[data-toast-undo]');
    u.hidden = !undo;
    undoFn = undo || null;
    toast.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.hidden = true; undoFn = null; }, undo ? 6000 : 3000);
  }
  toast.addEventListener('click', function (e) {
    if (e.target.closest('[data-toast-undo]') && undoFn) { undoFn(); undoFn = null; toast.hidden = true; }
  });

  function remove(id) {
    var it = store.items[id];
    if (!it) { return; }
    var before = it.data;
    put(id, before, true);
    say(KIND_LABEL[kindOf(before)] + ' deleted.', function () { put(id, before, false); });
  }

  /* ---------------------------------------------------------------- the sheet */

  var editing = null;   // { id } for an edit, { target, todo } for a new item
  var reopen = null;    // what the sheet opens next, once it has closed

  function where(d) {
    var parts = [];
    if (d.pageTitle) { parts.push(d.pageTitle); }
    if (d.section) { parts.push(d.section); }
    return parts.join(' › ');
  }

  function openSheet(opts) {
    editing = opts;
    var body = sheet.querySelector('#ann-body'), todo = sheet.querySelector('#ann-todo'), done = sheet.querySelector('#ann-done');
    var quote = sheet.querySelector('.ann-quote'), list = sheet.querySelector('.ann-existing');
    var d, title;
    if (opts.id) {
      d = store.items[opts.id].data;
      title = 'Edit ' + KIND_LABEL[kindOf(d)].toLowerCase();
    } else {
      d = fresh(opts.target, '', opts.todo);
      title = opts.todo ? 'New to-do' : (opts.target.quote ? 'New note' : 'Save this ' + (opts.target.anchor ? 'section' : 'page'));
    }
    sheet.querySelector('.ann-sheet-title').textContent = title;
    sheet.querySelector('.ann-where').textContent = where(d) || 'Not tied to a page';
    quote.hidden = !d.quote;
    quote.textContent = d.quote || '';
    body.value = d.body || '';
    todo.checked = !!d.todo;
    done.checked = !!d.done;
    sheet.querySelector('#ann-done-wrap').hidden = !d.todo;
    sheet.querySelector('.ann-danger').hidden = !opts.id;

    // A section's earlier bookmarks and notes, so the sheet never hides what is already saved.
    var others = opts.id || d.quote ? [] : marks().filter(function (it) {
      return it.data.page === d.page && !it.data.quote && (it.data.anchor || '') === (d.anchor || '');
    });
    list.hidden = !others.length;
    list.innerHTML = others.map(function (it) {
      return '<li><span class="ann-kind">' + KIND_LABEL[kindOf(it.data)] + '</span> ' +
        esc(it.data.body || 'No text') + ' <button type="button" data-sheet-edit="' + esc(it.id) + '">Edit</button></li>';
    }).join('');

    if (typeof sheet.showModal === 'function') { sheet.showModal(); } else { sheet.setAttribute('open', ''); }
    if (!(window.matchMedia && window.matchMedia('(hover: none)').matches)) { body.focus(); }
  }

  sheet.querySelector('#ann-todo').addEventListener('change', function (e) {
    sheet.querySelector('#ann-done-wrap').hidden = !e.target.checked;
  });
  sheet.addEventListener('click', function (e) {
    var b = e.target.closest('[data-sheet-edit]');
    if (b) { editing = null; reopen = { id: b.getAttribute('data-sheet-edit') }; sheet.close(); }
  });
  sheet.addEventListener('close', function () {
    var action = sheet.returnValue;
    sheet.returnValue = '';
    var opts = editing;
    editing = null;
    if (reopen) { var next = reopen; reopen = null; openSheet(next); return; }
    if (!opts) { return; }
    var body = sheet.querySelector('#ann-body').value.trim();
    var todo = sheet.querySelector('#ann-todo').checked;
    var done = todo && sheet.querySelector('#ann-done').checked;
    if (action === 'delete' && opts.id) { remove(opts.id); return; }
    if (action !== 'save') { return; }
    if (opts.id) {
      put(opts.id, Object.assign({}, store.items[opts.id].data, { body: body, todo: todo, done: done }), false);
      say('Saved.');
    } else {
      var n = fresh(opts.target, body, todo);
      n.done = done;
      put(newId(), n, false);
      say(KIND_LABEL[kindOf(n)] + ' saved.');
    }
  });

  document.addEventListener('click', function (e) {
    var t = e.target.nodeType === 1 ? e.target : e.target.parentElement;
    if (!t) { return; }
    var b;
    if ((b = t.closest('.ann-add, .ann-pill'))) {
      e.preventDefault();
      var anchor = b.getAttribute('data-ann-section');
      var section = anchor ? document.getElementById(anchor) : null;
      openSheet({ target: { anchor: anchor, section: headingOf(section) }, todo: false });
    } else if ((b = t.closest('mark.ann')) && !b.closest('a, summary')) {
      if (window.getSelection && !window.getSelection().isCollapsed) { return; }
      openSheet({ id: b.getAttribute('data-ann') });
    }
  });

  /* ---------------------------------------------------------------- the notes page */

  var filter = 'all';
  var tierOrder = {};
  (config.tiers || []).forEach(function (p, i) { tierOrder[p] = i; });

  function pageOrder(page) {
    if (!page) { return [-1, '']; }
    var m = /^([a-z])(\d\d)$/.exec(page);
    return m && m[1] in tierOrder ? [tierOrder[m[1]], m[2]] : [99, page];
  }

  function cardLink(it) {
    var d = it.data;
    if (!d.page) { return ''; }
    var href = d.page + '.html' + (d.quote ? '#ann-' + it.id : (d.anchor ? '#' + d.anchor : ''));
    return '<a href="' + esc(href) + '">' + esc(d.section || (d.quote ? 'Open the sentence' : 'Open the page')) + '</a>';
  }

  function card(it) {
    var d = it.data, k = kindOf(d);
    var date = new Date(d.created || it.updated).toLocaleDateString(lang, { day: 'numeric', month: 'short' });
    var lost = store.lost[it.id]
      ? '<p class="ann-lost">The text changed after you saved this, so it no longer shows on the page. ' +
        (d.quote ? 'The sentence you saved is above.' : 'Its section was renamed or removed.') + '</p>'
      : '';
    return '<li class="ann-card is-' + k + (d.done ? ' is-done' : '') + '" data-id="' + esc(it.id) + '">' +
      '<p class="ann-card-head"><span class="ann-kind">' + KIND_LABEL[k] + '</span>' + cardLink(it) +
      '<span class="ann-date">' + esc(date) + '</span></p>' +
      (d.quote ? '<blockquote class="ann-card-quote">' + esc(d.quote) + '</blockquote>' : '') +
      (d.body ? '<p class="ann-card-body">' + esc(d.body) + '</p>' : '') + lost +
      '<p class="ann-card-actions">' +
        (d.todo ? '<label><input type="checkbox" data-card-done' + (d.done ? ' checked' : '') + '> Done</label>' : '') +
        '<button type="button" data-card-edit>Edit</button><button type="button" data-card-delete>Delete</button></p></li>';
  }

  function renderNotesPage() {
    var box = document.querySelector('[data-notes-list]');
    if (!box) { return; }
    var all = marks();
    var counts = { all: all.length, bookmark: 0, note: 0, todo: 0, done: 0 };
    all.forEach(function (it) {
      var k = kindOf(it.data);
      if (k === 'todo' && it.data.done) { counts.done++; } else { counts[k]++; }
    });
    each('[data-notes-filter]', function (b) {
      var f = b.getAttribute('data-notes-filter');
      b.setAttribute('aria-pressed', f === filter ? 'true' : 'false');
      var c = b.querySelector('[data-count]');
      if (c) { c.textContent = counts[f]; }
    });
    var shown = all.filter(function (it) {
      var k = kindOf(it.data);
      if (filter === 'all') { return true; }
      if (filter === 'done') { return k === 'todo' && it.data.done; }
      if (filter === 'todo') { return k === 'todo' && !it.data.done; }
      return k === filter;
    });
    if (!shown.length) {
      box.innerHTML = '<p class="ann-empty">' + (all.length
        ? 'Nothing here under this filter.'
        : 'Nothing saved yet. To save a sentence, select it on any page. To save a section, use the + beside its heading.') + '</p>';
      return;
    }
    var groups = {};
    shown.forEach(function (it) { (groups[it.data.page || ''] = groups[it.data.page || ''] || []).push(it); });
    box.innerHTML = Object.keys(groups).sort(function (a, b) {
      var x = pageOrder(a), y = pageOrder(b);
      return x[0] - y[0] || (x[1] < y[1] ? -1 : x[1] > y[1] ? 1 : 0);
    }).map(function (page) {
      var list = groups[page].sort(function (a, b) {
        return (a.data.todo && a.data.done) - (b.data.todo && b.data.done) || (b.data.created || 0) - (a.data.created || 0);
      });
      var title = page ? '<a href="' + esc(page) + '.html">' + esc(list[0].data.pageTitle || page) + '</a>' : 'Your own to-dos';
      return '<section class="ann-group"><h2>' + title + '</h2><ol class="ann-list">' + list.map(card).join('') + '</ol></section>';
    }).join('');
  }

  function exportCopy() {
    var data = JSON.stringify(Object.keys(store.items).map(function (k) { return store.items[k]; })
      .filter(function (it) { return !it.deleted; }), null, 2);
    var a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([data], { type: 'application/json' }));
    a.download = prefix + '-notes-' + new Date().toISOString().slice(0, 10) + '.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.parentNode.removeChild(a); }, 1000);
  }

  // A downloaded copy merges into the store: for each item, the newer version wins.
  function importCopy(file) {
    var reader = new FileReader();
    reader.onload = function () {
      var list, added = 0;
      try { list = JSON.parse(reader.result); } catch (e) { list = null; }
      if (!Array.isArray(list)) { say('That file isn’t a copy of these notes.'); return; }
      list.forEach(function (it) {
        if (!it || typeof it.id !== 'string' || !it.data || typeof it.updated !== 'number') { return; }
        var mine = store.items[it.id];
        if (!mine || mine.updated < it.updated) {
          store.items[it.id] = { id: it.id, updated: it.updated, deleted: it.deleted ? 1 : 0, data: it.data };
          added++;
        }
      });
      persist();
      changed();
      say(added === 1 ? '1 item loaded.' : added + ' items loaded.');
    };
    reader.readAsText(file);
  }

  function initNotesPage() {
    var app = document.querySelector('[data-notes-app]');
    if (!app) { return; }
    app.hidden = false;
    each('[data-notes-noscript]', function (p) { p.hidden = true; });

    app.addEventListener('click', function (e) {
      var b, li = e.target.closest('.ann-card');
      if ((b = e.target.closest('[data-notes-filter]'))) {
        filter = b.getAttribute('data-notes-filter');
        renderNotesPage();
      } else if (li && e.target.closest('[data-card-edit]')) {
        openSheet({ id: li.getAttribute('data-id') });
      } else if (li && e.target.closest('[data-card-delete]')) {
        remove(li.getAttribute('data-id'));
      } else if (e.target.closest('[data-notes-export]')) {
        exportCopy();
      }
    });
    app.addEventListener('change', function (e) {
      var li = e.target.closest('.ann-card');
      if (li && e.target.matches('[data-card-done]')) {
        var id = li.getAttribute('data-id');
        put(id, Object.assign({}, store.items[id].data, { done: e.target.checked }), false);
      } else if (e.target.matches('[data-notes-import]') && e.target.files && e.target.files[0]) {
        importCopy(e.target.files[0]);
        e.target.value = '';
      }
    });

    var add = app.querySelector('[data-notes-add]');
    add.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = add.querySelector('input');
      var text = input.value.trim();
      if (!text) { return; }
      put(newId(), { kind: 'mark', page: '', pageTitle: '', anchor: '', section: '', quote: '', prefix: '', suffix: '',
                     body: text, todo: true, done: false, created: Date.now() }, false);
      input.value = '';
    });
    renderNotesPage();
  }

  /* ---------------------------------------------------------------- read marks, for site.js */

  window.GuideNotes = {
    isRead: function (id) { var it = store.items['read-' + id]; return !!(it && !it.deleted); },
    setRead: function (id, on) { put('read-' + id, { kind: 'read', page: String(id).toLowerCase() }, !on); },
    onChange: function (fn) { listeners.push(fn); }
  };

  /* ---------------------------------------------------------------- start */

  addHeadingButtons();
  paintPage();
  initNotesPage();
  paintState();
  revealHash();
  window.addEventListener('hashchange', revealHash);
  // Another tab of this guide changed the store: show its changes here too.
  window.addEventListener('storage', function (e) {
    if (e.key !== KEY_STORE) { return; }
    try {
      var next = JSON.parse(e.newValue || 'null');
      if (next && next.items) { store.items = next.items; store.lost = next.lost || {}; changed(); }
    } catch (err) { /* keep what we have */ }
  });
})();
