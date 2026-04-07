#!/usr/bin/python
# coding=utf-8
# Copyright 2026-Present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Web dashboard served at GET /."""

from bottle import response, route


_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Mongo Orchestration</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; }
    body { font-family: system-ui, -apple-system, sans-serif; max-width: 980px;
           margin: 40px auto; padding: 0 24px; color: #1a1a1a; background: #f5f5f5; }
    h1  { font-size: 1.5rem; margin-bottom: 4px; }
    h2  { font-size: 1rem; color: #555; margin: 28px 0 12px; font-weight: 600;
          text-transform: uppercase; letter-spacing: 0.05em; }
    .subtitle { font-size: 0.82rem; color: #999; margin-bottom: 28px; }
    code { font-family: ui-monospace, monospace; font-size: 0.85em;
           background: #ebebeb; padding: 1px 5px; border-radius: 3px; }

    /* ── Cards ─────────────────────────────────────────────────── */
    .card { background: #fff; border: 1px solid #e0e0e0; border-radius: 8px;
            margin-bottom: 12px; overflow: hidden; }

    .card-header { display: flex; align-items: center; gap: 10px;
                   padding: 12px 16px; border-bottom: 1px solid #f0f0f0; }
    .card-header .id   { font-family: ui-monospace, monospace; font-size: 0.85rem;
                         flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .card-header .uri  { font-family: ui-monospace, monospace; font-size: 0.8rem;
                         color: #555; flex: 2; min-width: 0; word-break: break-all; }
    .stop-btn { margin-left: auto; flex-shrink: 0; background: #fee2e2; color: #b91c1c;
                border: 1px solid #fca5a5; border-radius: 4px; padding: 4px 10px;
                font-size: 0.8rem; cursor: pointer; }
    .stop-btn:hover { background: #fecaca; }
    .add-btn { flex-shrink: 0; background: #f0fdf4; color: #15803d; border: 1px solid #86efac;
               border-radius: 4px; padding: 4px 10px; font-size: 0.8rem; cursor: pointer; }
    .add-btn:hover { background: #dcfce7; }
    .remove-btn { margin-left: auto; flex-shrink: 0; background: #fef9c3; color: #92400e;
                  border: 1px solid #fde68a; border-radius: 4px; padding: 2px 7px;
                  font-size: 0.75rem; cursor: pointer; }
    .remove-btn:hover { background: #fef3c7; }

    /* ── Nested members ─────────────────────────────────────────── */
    .members { padding: 0 16px 8px; }
    .section-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
                     letter-spacing: 0.06em; color: #aaa; margin: 10px 0 4px; }
    .member { display: flex; align-items: center; gap: 10px; padding: 4px 0;
              border-bottom: 1px solid #f5f5f5; font-size: 0.85rem; }
    .member:last-child { border-bottom: none; }
    .member .host { font-family: ui-monospace, monospace; color: #333; }
    .member .member-uri { font-family: ui-monospace, monospace; font-size: 0.8rem; color: #777; }

    /* ── Badges ─────────────────────────────────────────────────── */
    .badge { display: inline-block; padding: 2px 8px; border-radius: 20px;
             font-size: 0.72rem; font-weight: 700; letter-spacing: 0.03em; flex-shrink: 0; }
    .badge-single  { background: #dbeafe; color: #1d4ed8; }
    .badge-repl    { background: #dcfce7; color: #15803d; }
    .badge-shard   { background: #fef9c3; color: #a16207; }
    .badge-configsvr { background: #f3e8ff; color: #7e22ce; }
    .badge-mongos  { background: #e0f2fe; color: #0369a1; }
    .version { font-size: 0.75rem; color: #888; background: #f3f4f6; padding: 2px 7px;
               border-radius: 20px; flex-shrink: 0; }

    .role { display: inline-block; padding: 1px 7px; border-radius: 3px;
            font-size: 0.7rem; font-weight: 700; letter-spacing: 0.04em; flex-shrink: 0; min-width: 76px; text-align: center; }
    .role-primary   { background: #dcfce7; color: #15803d; }
    .role-secondary { background: #e0f2fe; color: #0369a1; }
    .role-arbiter   { background: #fef9c3; color: #a16207; }
    .role-other     { background: #f3f4f6; color: #6b7280; }

    .empty { color: #aaa; font-style: italic; font-size: 0.9rem; padding: 8px 0; }

    /* ── Form ───────────────────────────────────────────────────── */
    .form-card { background: #fff; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px 20px; }
    .form-row  { display: flex; flex-wrap: wrap; gap: 14px; align-items: flex-end; }
    .field     { display: flex; flex-direction: column; gap: 4px; }
    .field > span { font-size: 0.78rem; font-weight: 600; color: #666; }
    select, input[type=text] { padding: 7px 10px; border: 1px solid #d1d5db; border-radius: 5px;
                               font-size: 0.88rem; background: #fff; }
    .checkboxes { display: flex; gap: 16px; align-items: center; padding-bottom: 2px; }
    .checkboxes label { display: flex; align-items: center; gap: 5px;
                        font-size: 0.85rem; cursor: pointer; }
    button[type=submit] { background: #1d4ed8; color: #fff; border: none; padding: 8px 18px;
                          border-radius: 5px; font-size: 0.9rem; cursor: pointer; }
    button[type=submit]:hover { background: #1e40af; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }

    #result { margin-top: 12px; padding: 10px 14px; border-radius: 6px;
              font-family: ui-monospace, monospace; font-size: 0.82rem;
              display: none; white-space: pre-wrap; }
    #result.success { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
    #result.error   { background: #fee2e2; color: #b91c1c; border: 1px solid #fca5a5; }

    .refresh-info { font-size: 0.75rem; color: #bbb; margin-left: 6px; font-weight: 400; }
  </style>
</head>
<body>
  <h1>Mongo Orchestration</h1>
  <p class="subtitle">REST API at <code>/v1/</code></p>

  <h2>Running clusters <span id="refresh-info" class="refresh-info"></span></h2>
  <div id="cluster-list"><p class="empty">Loading\u2026</p></div>

  <h2>Start a new cluster</h2>
  <div class="form-card">
    <form id="launch-form">
      <div class="form-row">
        <div class="field">
          <span>Type</span>
          <select id="cluster_type" name="cluster_type">
            <option value="single">Standalone</option>
            <option value="repl">Replica Set (3 members)</option>
            <option value="shard">Sharded Cluster</option>
          </select>
        </div>
        <div class="field">
          <span>Version</span>
          <select id="version" name="version">
            <option value="">default</option>
          </select>
        </div>
        <div class="checkboxes">
          <label><input type="checkbox" name="single_member" id="single_member"> Single member</label>
          <label><input type="checkbox" name="auth"> Auth</label>
          <label><input type="checkbox" name="ssl"> SSL</label>
        </div>
        <button type="submit" id="start-btn">Start</button>
      </div>
    </form>
    <div id="result"></div>
  </div>

  <script>
    const RESOURCES = [
      { path: 'servers',          key: 'servers',          label: 'Standalone',      badge: 'badge-single' },
      { path: 'replica_sets',     key: 'replica_sets',     label: 'Replica Set',     badge: 'badge-repl'   },
      { path: 'sharded_clusters', key: 'sharded_clusters', label: 'Sharded Cluster', badge: 'badge-shard'  },
    ];

    const STATE_LABELS = { 1: 'PRIMARY', 2: 'SECONDARY', 7: 'ARBITER' };
    const STATE_CLASSES = { 1: 'role-primary', 2: 'role-secondary', 7: 'role-arbiter' };

    function esc(s) {
      return String(s ?? '').replace(/[&<>"']/g, c =>
        ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
    }

    async function api(path, opts) {
      const r = await fetch('/v1/' + path, opts);
      return { ok: r.ok, data: await r.json().catch(() => null) };
    }

    // ── Renderers ─────────────────────────────────────────────────────────

    function renderMemberRole(state) {
      const label = STATE_LABELS[state] ?? ('state ' + state);
      const cls   = STATE_CLASSES[state] ?? 'role-other';
      return '<span class="role ' + cls + '">' + label + '</span>';
    }

    function renderRsMembers(rsId, members, removable) {
      if (!members?.length) return '';
      return members.map(m =>
        '<div class="member">'
        + renderMemberRole(m.state)
        + '<span class="host">' + esc(m.host) + '</span>'
        + (m._uri ? '<span class="member-uri">' + esc(m._uri) + '</span>' : '')
        + (removable
          ? '<button class="remove-btn" data-action="remove-member"'
            + ' data-rs="' + esc(rsId) + '" data-member="' + m._id + '">Remove</button>'
          : '')
        + '</div>'
      ).join('');
    }

    function renderVersion(v) {
      return v ? '<span class="version">' + esc(v) + '</span>' : '';
    }

    function renderServer(d) {
      const uri = d.mongodb_auth_uri || d.mongodb_uri || '';
      const ver = d.serverInfo?.version || '';
      return '<div class="card">'
        + '<div class="card-header">'
        + '<span class="badge badge-single">Standalone</span>'
        + '<span class="id">' + esc(d.id) + '</span>'
        + renderVersion(ver)
        + '<span class="uri">' + esc(uri) + '</span>'
        + '<button class="stop-btn" data-action="stop" data-res="servers" data-id="' + esc(d.id) + '">Stop</button>'
        + '</div></div>';
    }

    function renderReplicaSet(d) {
      const uri = d.mongodb_auth_uri || d.mongodb_uri || '';
      const ver = d._version || '';
      return '<div class="card">'
        + '<div class="card-header">'
        + '<span class="badge badge-repl">Replica Set</span>'
        + '<span class="id">' + esc(d.id) + '</span>'
        + renderVersion(ver)
        + '<span class="uri">' + esc(uri) + '</span>'
        + '<button class="add-btn" data-action="add-member" data-rs="' + esc(d.id) + '">+ Member</button>'
        + '<button class="stop-btn" data-action="stop" data-res="replica_sets" data-id="' + esc(d.id) + '">Stop</button>'
        + '</div>'
        + '<div class="members">' + renderRsMembers(d.id, d.members, true) + '</div>'
        + '</div>';
    }

    function renderShardedCluster(d) {
      const uri = d.mongodb_auth_uri || d.mongodb_uri || '';
      const ver = d._version || '';
      let inner = '';

      if (d.routers?.length) {
        inner += '<div class="section-label">Mongos routers</div>';
        inner += d.routers.map(r =>
          '<div class="member">'
          + '<span class="badge badge-mongos">mongos</span>'
          + '<span class="host">' + esc(r.hostname || r.id) + '</span>'
          + (r._uri ? '<span class="member-uri">' + esc(r._uri) + '</span>' : '')
          + '<button class="remove-btn" data-action="remove-router"'
          + ' data-cluster="' + esc(d.id) + '" data-router="' + esc(r.id) + '">Remove</button>'
          + '</div>'
        ).join('');
      }

      if (d.configsvrs?.length) {
        inner += '<div class="section-label">Config servers</div>';
        inner += d.configsvrs.map(c =>
          '<div class="member">'
          + '<span class="badge badge-configsvr">configsvr</span>'
          + '<span class="member-uri">' + esc(c.mongodb_uri || c.id) + '</span>'
          + '</div>'
        ).join('');
      }

      if (d.shards?.length) {
        inner += '<div class="section-label">Shards</div>';
        inner += d.shards.map(sh => {
          let shHtml = '<div class="member" style="flex-wrap:wrap;gap:4px;">'
            + '<span class="badge badge-repl">' + esc(sh.id) + '</span>'
            + '<button class="remove-btn" data-action="remove-shard"'
            + ' data-cluster="' + esc(d.id) + '" data-shard="' + esc(sh.id) + '">Remove</button>'
            + '</div>';
          if (sh._rsMembers?.length) {
            shHtml += '<div style="padding-left:24px;">'
              + renderRsMembers(sh._id, sh._rsMembers, false)
              + '</div>';
          }
          return shHtml;
        }).join('');
      }

      return '<div class="card">'
        + '<div class="card-header">'
        + '<span class="badge badge-shard">Sharded Cluster</span>'
        + '<span class="id">' + esc(d.id) + '</span>'
        + renderVersion(ver)
        + '<span class="uri">' + esc(uri) + '</span>'
        + '<button class="add-btn" data-action="add-router" data-cluster="' + esc(d.id) + '">+ Router</button>'
        + '<button class="add-btn" data-action="add-shard" data-cluster="' + esc(d.id) + '">+ Shard</button>'
        + '<button class="stop-btn" data-action="stop" data-res="sharded_clusters" data-id="' + esc(d.id) + '">Stop</button>'
        + '</div>'
        + '<div class="members">' + inner + '</div>'
        + '</div>';
    }

    // ── Data loading ───────────────────────────────────────────────────────

    async function serverDetail(id) {
      try { return (await api('servers/' + id)).data; } catch { return null; }
    }

    async function enrichMembers(members) {
      // Fetch server details for each RS member, attach _uri and track server IDs.
      const ids = new Set();
      await Promise.all((members ?? []).map(async m => {
        if (!m.server_id) return;
        ids.add(m.server_id);
        const sv = await serverDetail(m.server_id);
        m._uri = sv?.mongodb_auth_uri || sv?.mongodb_uri || '';
        m._version = sv?.serverInfo?.version || '';
      }));
      return ids;
    }

    async function loadClusters() {
      document.getElementById('refresh-info').textContent = 'refreshing\u2026';
      const usedServerIds = new Set();
      const rsParts = [];
      const shardParts = [];

      // ── Replica sets ─────────────────────────────────────────────────
      try {
        const { data } = await api('replica_sets');
        for (const item of data?.replica_sets ?? []) {
          const { data: d } = await api('replica_sets/' + item.id);
          if (!d) continue;
          const ids = await enrichMembers(d.members);
          ids.forEach(id => usedServerIds.add(id));
          const ref = d.members?.find(m => m.state === 1) ?? d.members?.[0];
          d._version = ref?._version || '';
          rsParts.push(renderReplicaSet(d));
        }
      } catch { /* unreachable */ }

      // ── Sharded clusters ─────────────────────────────────────────────
      try {
        const { data } = await api('sharded_clusters');
        for (const item of data?.sharded_clusters ?? []) {
          const { data: d } = await api('sharded_clusters/' + item.id);
          if (!d) continue;

          // Enrich routers
          await Promise.all((d.routers ?? []).map(async r => {
            usedServerIds.add(r.id);
            const sv = await serverDetail(r.id);
            r._uri = sv?.mongodb_uri || '';
            if (!d._version && sv?.serverInfo?.version) d._version = sv.serverInfo.version;
          }));

          // Track config servers
          (d.configsvrs ?? []).forEach(c => usedServerIds.add(c.id));

          // Enrich shard RS members
          for (const sh of d.shards ?? []) {
            if (sh.isReplicaSet && sh._id) {
              try {
                const { data: rs } = await api('replica_sets/' + sh._id);
                sh._rsMembers = rs?.members ?? [];
                const ids = await enrichMembers(sh._rsMembers);
                ids.forEach(id => usedServerIds.add(id));
              } catch { /* ignore */ }
            }
          }
          shardParts.push(renderShardedCluster(d));
        }
      } catch { /* unreachable */ }

      // ── Standalone servers (exclude members of clusters) ─────────────
      const standaloneParts = [];
      try {
        const { data } = await api('servers');
        for (const item of data?.servers ?? []) {
          if (usedServerIds.has(item.id)) continue;
          const { data: d } = await api('servers/' + item.id);
          if (d) standaloneParts.push(renderServer(d));
        }
      } catch { /* unreachable */ }

      const parts = [...standaloneParts, ...rsParts, ...shardParts];
      const el = document.getElementById('cluster-list');
      el.innerHTML = parts.length
        ? parts.join('')
        : '<p class="empty">No clusters running.</p>';

      el.addEventListener('click', async e => {
        const btn = e.target.closest('button[data-action]');
        if (!btn || btn.disabled) return;
        const { action, res, id, rs, member, cluster, router, shard } = btn.dataset;
        btn.disabled = true;

        const post = (path, body = {}) => api(path, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });

        if (action === 'stop') {
          if (!confirm('Stop ' + id + '?')) { btn.disabled = false; return; }
          await api(res + '/' + id, { method: 'DELETE' });

        } else if (action === 'add-member') {
          await post('replica_sets/' + rs + '/members', { procParams: {} });

        } else if (action === 'remove-member') {
          if (!confirm('Remove member ' + member + '?')) { btn.disabled = false; return; }
          await api('replica_sets/' + rs + '/members/' + member, { method: 'DELETE' });

        } else if (action === 'add-router') {
          await post('sharded_clusters/' + cluster + '/routers', {});

        } else if (action === 'remove-router') {
          if (!confirm('Remove router ' + router + '?')) { btn.disabled = false; return; }
          await api('sharded_clusters/' + cluster + '/routers/' + router, { method: 'DELETE' });

        } else if (action === 'add-shard') {
          await post('sharded_clusters/' + cluster + '/shards', { procParams: {} });

        } else if (action === 'remove-shard') {
          if (!confirm('Remove shard ' + shard + '?')) { btn.disabled = false; return; }
          await api('sharded_clusters/' + cluster + '/shards/' + shard, { method: 'DELETE' });
        }

        loadClusters();
      });

      document.getElementById('refresh-info').textContent =
        'updated ' + new Date().toLocaleTimeString();
    }

    async function loadVersions() {
      try {
        const { data } = await api('releases');
        const sel = document.getElementById('version');
        for (const v of Object.keys(data?.releases ?? {})) {
          const opt = document.createElement('option');
          opt.value = v; opt.textContent = v;
          sel.appendChild(opt);
        }
      } catch { /* ignore */ }
    }

    document.getElementById('cluster_type').addEventListener('change', function () {
      document.getElementById('single_member').disabled = this.value === 'single';
    });

    document.getElementById('launch-form').addEventListener('submit', async e => {
      e.preventDefault();
      const btn = document.getElementById('start-btn');
      btn.disabled = true; btn.textContent = 'Starting\u2026';

      const fd = new FormData(e.target);
      const clusterType  = fd.get('cluster_type');
      const version      = fd.get('version');
      const auth         = fd.get('auth') === 'on';
      const singleMember = fd.get('single_member') === 'on';

      const base = {};
      if (version) base.version = version;
      if (auth) { base.login = 'user'; base.password = 'password'; base.auth_key = 'secret'; }

      const n = singleMember ? 1 : 3;
      let path, body;
      if (clusterType === 'single') {
        path = 'servers';
        body = { ...base, name: 'mongod', procParams: {} };
      } else if (clusterType === 'repl') {
        path = 'replica_sets';
        body = { ...base, members: Array.from({ length: n }, () => ({ procParams: {} })) };
      } else {
        path = 'sharded_clusters';
        body = { ...base, configsvrs: [{}], routers: [{}],
          shards: [{ id: 'shard-0', shardParams: {
            members: Array.from({ length: n }, () => ({ procParams: {} })) } }] };
      }

      const resultEl = document.getElementById('result');
      try {
        const { ok, data } = await api(path, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body),
        });
        if (ok) {
          const uri = data?.mongodb_auth_uri || data?.mongodb_uri || '';
          resultEl.className = 'success';
          resultEl.textContent = 'Started  id: ' + data?.id + '\\n         uri: ' + uri;
          loadClusters();
        } else {
          resultEl.className = 'error';
          resultEl.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
        }
      } catch (err) {
        resultEl.className = 'error';
        resultEl.textContent = 'Error: ' + err.message;
      }
      resultEl.style.display = 'block';
      btn.disabled = false; btn.textContent = 'Start';
    });

    loadVersions();
    loadClusters();
    setInterval(loadClusters, 5000);
  </script>
</body>
</html>
"""


@route('/')
def dashboard():
    response.content_type = 'text/html; charset=utf-8'
    return _HTML
