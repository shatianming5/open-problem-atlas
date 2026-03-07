/**
 * OpenProblemAtlas — Force-directed graph visualization (pure JS, no D3)
 */

(function() {
  'use strict';

  var DOMAIN_COLORS = {
    'mathematics': '#58a6ff',
    'theoretical-cs': '#3fb950',
    'mathematical-physics': '#d29922'
  };
  var DEFAULT_COLOR = '#bc8cff';
  var EDGE_COLOR = 'rgba(48, 54, 61, 0.7)';
  var NODE_RADIUS = 8;
  var LABEL_FONT = '11px -apple-system, BlinkMacSystemFont, sans-serif';

  var canvas = document.getElementById('graph-canvas');
  var ctx = canvas.getContext('2d');
  var container = document.getElementById('graph-container');
  var tooltip = document.getElementById('graph-tooltip');

  var data = (typeof GRAPH_DATA !== 'undefined') ? GRAPH_DATA : { nodes: [], edges: [] };
  var nodes = [];
  var edges = [];
  var nodeMap = {};

  var dragging = null;
  var hovering = null;
  var offsetX = 0, offsetY = 0;
  var animId = null;

  function init() {
    resize();
    window.addEventListener('resize', resize);

    var w = canvas.width;
    var h = canvas.height;
    var cx = w / 2;
    var cy = h / 2;

    // Create node objects
    data.nodes.forEach(function(n, i) {
      var angle = (2 * Math.PI * i) / data.nodes.length;
      var r = Math.min(w, h) * 0.3;
      var node = {
        id: n.id,
        title: n.title,
        domain: n.domain,
        slug: n.slug,
        x: cx + r * Math.cos(angle) + (Math.random() - 0.5) * 50,
        y: cy + r * Math.sin(angle) + (Math.random() - 0.5) * 50,
        vx: 0,
        vy: 0,
        color: DOMAIN_COLORS[n.domain] || DEFAULT_COLOR
      };
      nodes.push(node);
      nodeMap[n.id] = node;
    });

    // Create edge objects
    data.edges.forEach(function(e) {
      var source = nodeMap[e.source];
      var target = nodeMap[e.target];
      if (source && target) {
        edges.push({ source: source, target: target, label: e.label || '' });
      }
    });

    canvas.addEventListener('mousedown', onMouseDown);
    canvas.addEventListener('mousemove', onMouseMove);
    canvas.addEventListener('mouseup', onMouseUp);
    canvas.addEventListener('mouseleave', onMouseUp);
    canvas.addEventListener('click', onClick);

    animate();
  }

  function resize() {
    var rect = container.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
  }

  function animate() {
    simulate();
    draw();
    animId = requestAnimationFrame(animate);
  }

  function simulate() {
    var damping = 0.92;
    var repulsion = 2000;
    var attraction = 0.005;
    var idealLen = 150;
    var centerGravity = 0.01;
    var cx = canvas.width / 2;
    var cy = canvas.height / 2;

    // Repulsion between all pairs
    for (var i = 0; i < nodes.length; i++) {
      for (var j = i + 1; j < nodes.length; j++) {
        var dx = nodes[j].x - nodes[i].x;
        var dy = nodes[j].y - nodes[i].y;
        var dist = Math.sqrt(dx * dx + dy * dy) || 1;
        var force = repulsion / (dist * dist);
        var fx = (dx / dist) * force;
        var fy = (dy / dist) * force;
        nodes[i].vx -= fx;
        nodes[i].vy -= fy;
        nodes[j].vx += fx;
        nodes[j].vy += fy;
      }
    }

    // Attraction along edges
    edges.forEach(function(e) {
      var dx = e.target.x - e.source.x;
      var dy = e.target.y - e.source.y;
      var dist = Math.sqrt(dx * dx + dy * dy) || 1;
      var force = (dist - idealLen) * attraction;
      var fx = (dx / dist) * force;
      var fy = (dy / dist) * force;
      e.source.vx += fx;
      e.source.vy += fy;
      e.target.vx -= fx;
      e.target.vy -= fy;
    });

    // Center gravity
    nodes.forEach(function(n) {
      n.vx += (cx - n.x) * centerGravity;
      n.vy += (cy - n.y) * centerGravity;
    });

    // Update positions
    nodes.forEach(function(n) {
      if (n === dragging) return;
      n.vx *= damping;
      n.vy *= damping;
      n.x += n.vx;
      n.y += n.vy;
      // Keep in bounds
      n.x = Math.max(NODE_RADIUS, Math.min(canvas.width - NODE_RADIUS, n.x));
      n.y = Math.max(NODE_RADIUS, Math.min(canvas.height - NODE_RADIUS, n.y));
    });
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw edges
    ctx.strokeStyle = EDGE_COLOR;
    ctx.lineWidth = 1;
    edges.forEach(function(e) {
      ctx.beginPath();
      ctx.moveTo(e.source.x, e.source.y);
      ctx.lineTo(e.target.x, e.target.y);
      ctx.stroke();
    });

    // Draw nodes
    nodes.forEach(function(n) {
      var r = (n === hovering) ? NODE_RADIUS + 3 : NODE_RADIUS;
      ctx.beginPath();
      ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
      ctx.fillStyle = n.color;
      ctx.fill();
      if (n === hovering) {
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();
      }
    });

    // Draw labels
    ctx.font = LABEL_FONT;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    nodes.forEach(function(n) {
      ctx.fillStyle = 'rgba(230, 237, 243, 0.8)';
      var label = n.title.length > 20 ? n.title.substring(0, 18) + '..' : n.title;
      ctx.fillText(label, n.x, n.y + NODE_RADIUS + 4);
    });
  }

  function getNodeAt(mx, my) {
    for (var i = nodes.length - 1; i >= 0; i--) {
      var dx = mx - nodes[i].x;
      var dy = my - nodes[i].y;
      if (dx * dx + dy * dy <= (NODE_RADIUS + 4) * (NODE_RADIUS + 4)) {
        return nodes[i];
      }
    }
    return null;
  }

  function getMousePos(e) {
    var rect = canvas.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  }

  function onMouseDown(e) {
    var pos = getMousePos(e);
    var node = getNodeAt(pos.x, pos.y);
    if (node) {
      dragging = node;
      offsetX = pos.x - node.x;
      offsetY = pos.y - node.y;
      node.vx = 0;
      node.vy = 0;
    }
  }

  function onMouseMove(e) {
    var pos = getMousePos(e);
    if (dragging) {
      dragging.x = pos.x - offsetX;
      dragging.y = pos.y - offsetY;
      dragging.vx = 0;
      dragging.vy = 0;
    }

    var node = getNodeAt(pos.x, pos.y);
    hovering = node;
    canvas.style.cursor = node ? 'pointer' : 'grab';

    if (node) {
      tooltip.style.display = 'block';
      tooltip.querySelector('.tip-title').textContent = node.title;
      tooltip.querySelector('.tip-domain').textContent = node.domain.replace(/-/g, ' ');
      var tx = pos.x + 16;
      var ty = pos.y + 16;
      if (tx + 250 > canvas.width) tx = pos.x - 260;
      if (ty + 60 > canvas.height) ty = pos.y - 70;
      tooltip.style.left = tx + 'px';
      tooltip.style.top = ty + 'px';
    } else {
      tooltip.style.display = 'none';
    }
  }

  function onMouseUp() {
    dragging = null;
  }

  function onClick(e) {
    var pos = getMousePos(e);
    var node = getNodeAt(pos.x, pos.y);
    if (node && node.slug) {
      window.location.href = '/problem/' + node.slug + '.html';
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
