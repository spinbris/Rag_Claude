"""Visualization utilities for knowledge graphs."""

from typing import List, Dict, Tuple, Optional
import json


class GraphVisualizer:
    """Visualize knowledge graphs in various formats."""

    @staticmethod
    def to_mermaid(entities: List[str], relations: List[Tuple[str, str, str]]) -> str:
        """
        Convert graph to Mermaid diagram format.

        Args:
            entities: List of entity names
            relations: List of (source, relation, target) tuples

        Returns:
            Mermaid diagram as string
        """
        mermaid = "graph TD\n"

        # Create node IDs (replace spaces with underscores)
        entity_ids = {e: e.replace(' ', '_').replace('-', '_') for e in entities}

        # Add nodes
        for entity, node_id in entity_ids.items():
            mermaid += f'    {node_id}["{entity}"]\n'

        # Add edges
        for source, relation, target in relations:
            source_id = entity_ids.get(source, source.replace(' ', '_'))
            target_id = entity_ids.get(target, target.replace(' ', '_'))
            mermaid += f'    {source_id} -->|{relation}| {target_id}\n'

        return mermaid

    @staticmethod
    def to_networkx(entities: List[str], relations: List[Tuple[str, str, str]]):
        """
        Convert graph to NetworkX graph object.

        Args:
            entities: List of entity names
            relations: List of (source, relation, target) tuples

        Returns:
            NetworkX DiGraph object
        """
        try:
            import networkx as nx
        except ImportError:
            raise ImportError("networkx is required for graph visualization. Install with: uv add networkx")

        G = nx.DiGraph()

        # Add nodes
        for entity in entities:
            G.add_node(entity)

        # Add edges
        for source, relation, target in relations:
            G.add_edge(source, target, relation=relation)

        return G

    @staticmethod
    def to_cytoscape(entities: List[str], relations: List[Tuple[str, str, str]]) -> Dict:
        """
        Convert graph to Cytoscape.js format.

        Args:
            entities: List of entity names
            relations: List of (source, relation, target) tuples

        Returns:
            Dict in Cytoscape.js format
        """
        cytoscape_data = {
            "nodes": [],
            "edges": []
        }

        # Add nodes
        for entity in entities:
            cytoscape_data["nodes"].append({
                "data": {
                    "id": entity,
                    "label": entity
                }
            })

        # Add edges
        for i, (source, relation, target) in enumerate(relations):
            cytoscape_data["edges"].append({
                "data": {
                    "id": f"edge_{i}",
                    "source": source,
                    "target": target,
                    "label": relation
                }
            })

        return cytoscape_data

    @staticmethod
    def to_ascii_art(entities: Dict[str, int], relations: List[Tuple[str, str, str]], max_entities: int = 20) -> str:
        """
        Create simple ASCII art representation of the graph.

        Args:
            entities: Dict mapping entity names to occurrence counts
            relations: List of (source, relation, target) tuples
            max_entities: Maximum number of entities to show

        Returns:
            ASCII art string
        """
        # Get top entities by frequency
        top_entities = sorted(entities.items(), key=lambda x: x[1], reverse=True)[:max_entities]

        ascii_art = "Knowledge Graph Summary\n"
        ascii_art += "=" * 60 + "\n\n"

        # Show top entities
        ascii_art += "Top Entities:\n"
        ascii_art += "-" * 60 + "\n"
        for entity, count in top_entities:
            bar = "█" * min(count, 50)
            ascii_art += f"{entity:30s} {bar} ({count})\n"

        # Show relationships
        ascii_art += "\n" + "=" * 60 + "\n"
        ascii_art += "Relationships:\n"
        ascii_art += "-" * 60 + "\n"

        # Group relations by type
        relation_types = {}
        for source, relation, target in relations:
            if relation not in relation_types:
                relation_types[relation] = []
            relation_types[relation].append((source, target))

        for rel_type, pairs in sorted(relation_types.items()):
            ascii_art += f"\n[{rel_type}] ({len(pairs)} relations):\n"
            for source, target in pairs[:5]:  # Show first 5 of each type
                ascii_art += f"  • {source} → {target}\n"
            if len(pairs) > 5:
                ascii_art += f"  ... and {len(pairs) - 5} more\n"

        return ascii_art

    @staticmethod
    def save_html_visualization(entities: List[str], relations: List[Tuple[str, str, str]], filepath: str):
        """
        Save an interactive HTML visualization using D3.js.

        Args:
            entities: List of entity names
            relations: List of (source, relation, target) tuples
            filepath: Output file path
        """
        # Convert to node-link format
        nodes = [{"id": e, "label": e} for e in entities]
        links = [{"source": s, "target": t, "label": r} for s, r, t in relations]

        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Knowledge Graph Visualization</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        #graph {{
            width: 100%;
            height: 800px;
            border: 1px solid #ccc;
            background: white;
        }}
        .node {{
            cursor: pointer;
        }}
        .node circle {{
            fill: #4CAF50;
            stroke: #2E7D32;
            stroke-width: 2px;
        }}
        .node text {{
            font-size: 12px;
            pointer-events: none;
        }}
        .link {{
            stroke: #999;
            stroke-opacity: 0.6;
            stroke-width: 1.5px;
        }}
        .link-label {{
            font-size: 10px;
            fill: #666;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        .stats {{
            text-align: center;
            margin-bottom: 20px;
            color: #666;
        }}
    </style>
</head>
<body>
    <h1>Knowledge Graph Visualization</h1>
    <div class="stats">
        <strong>Entities:</strong> {num_entities} |
        <strong>Relationships:</strong> {num_relations}
    </div>
    <svg id="graph"></svg>

    <script>
        const graphData = {{
            nodes: {nodes_json},
            links: {links_json}
        }};

        const width = document.getElementById('graph').clientWidth;
        const height = 800;

        const svg = d3.select("#graph")
            .attr("width", width)
            .attr("height", height);

        const simulation = d3.forceSimulation(graphData.nodes)
            .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const link = svg.append("g")
            .selectAll("line")
            .data(graphData.links)
            .enter().append("line")
            .attr("class", "link");

        const linkLabel = svg.append("g")
            .selectAll("text")
            .data(graphData.links)
            .enter().append("text")
            .attr("class", "link-label")
            .text(d => d.label);

        const node = svg.append("g")
            .selectAll("g")
            .data(graphData.nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("circle")
            .attr("r", 8);

        node.append("text")
            .attr("dx", 12)
            .attr("dy", 4)
            .text(d => d.label);

        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            linkLabel
                .attr("x", d => (d.source.x + d.target.x) / 2)
                .attr("y", d => (d.source.y + d.target.y) / 2);

            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>
        """

        html_content = html_template.format(
            nodes_json=json.dumps(nodes),
            links_json=json.dumps(links),
            num_entities=len(entities),
            num_relations=len(relations)
        )

        with open(filepath, 'w') as f:
            f.write(html_content)

        print(f"Interactive visualization saved to {filepath}")
