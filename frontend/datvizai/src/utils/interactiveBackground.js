export function initInteractiveBackground(canvas) {
	const ctx = canvas.getContext("2d");
  
	// Set canvas dimensions
	canvas.width = window.innerWidth;
	canvas.height = window.innerHeight;
  
	const nodes = [];
	const maxNodes = 100;
  
	// Create random nodes
	for (let i = 0; i < maxNodes; i++) {
	  nodes.push({
		x: Math.random() * canvas.width,
		y: Math.random() * canvas.height,
		radius: 2 + Math.random() * 2,
		dx: Math.random() * 2 - 1,
		dy: Math.random() * 2 - 1,
	  });
	}
  
	// Draw nodes
	function drawNodes() {
	  ctx.clearRect(0, 0, canvas.width, canvas.height);
	  ctx.fillStyle = "#ffffff";
  
	  nodes.forEach((node) => {
		ctx.beginPath();
		ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
		ctx.fill();
		ctx.closePath();
	  });
	}
  
	// Draw connections
	function drawConnections() {
	  ctx.strokeStyle = "#ffffff";
	  ctx.lineWidth = 0.5;
  
	  nodes.forEach((node, idx) => {
		for (let j = idx + 1; j < nodes.length; j++) {
		  const distance = Math.sqrt(
			Math.pow(nodes[j].x - node.x, 2) + Math.pow(nodes[j].y - node.y, 2)
		  );
  
		  if (distance < 100) {
			ctx.beginPath();
			ctx.moveTo(node.x, node.y);
			ctx.lineTo(nodes[j].x, nodes[j].y);
			ctx.stroke();
			ctx.closePath();
		  }
		}
	  });
	}
  
	// Update node positions
	function updateNodes() {
	  nodes.forEach((node) => {
		node.x += node.dx;
		node.y += node.dy;
  
		// Bounce nodes off edges
		if (node.x < 0 || node.x > canvas.width) node.dx *= -1;
		if (node.y < 0 || node.y > canvas.height) node.dy *= -1;
	  });
	}
  
	// Animation loop
	function animate() {
	  drawNodes();
	  drawConnections();
	  updateNodes();
	  requestAnimationFrame(animate);
	}
  
	animate();
  
	// Handle canvas resizing
	window.addEventListener("resize", () => {
	  canvas.width = window.innerWidth;
	  canvas.height = window.innerHeight;
	});
  }
  