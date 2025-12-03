/**
 * ═══════════════════════════════════════════════════════════════════
 * CONGRESS TWITTER NETWORK ANALYTICS DASHBOARD - JAVASCRIPT
 * ═══════════════════════════════════════════════════════════════════
 * 
 * SOCIAL NETWORK ANALYSIS OF U.S. CONGRESS
 */

// ═══════════════════════════════════════════════════════════════════
// 1. COLOR CONFIGURATION AND CONSTANTS
// ═══════════════════════════════════════════════════════════════════

const communityColors = {
    '0': '#667eea',
    '1': '#f56565',
    '2': '#48bb78',
    '3': '#ed8936',
    '4': '#9f7aea'
};

const centralityColors = {
    'pagerank': '#9f7aea',
    'betweenness': '#ed8936',
    'indegree': '#4299e1',
    'outdegree': '#38b2ac'
};

const centralityDescriptions = {
    'pagerank': 'Ranking of most influential Congress members by PageRank. This metric identifies members who are connected to other highly connected members, indicating overall network importance.',
    'betweenness': 'Ranking of most influential Congress members by Betweenness Centrality. This metric identifies members who act as bridges between different groups, controlling information flow.',
    'indegree': 'Ranking of most influential Congress members by In-Degree. This metric shows members who receive the most attention or connections from others.',
    'outdegree': 'Ranking of most influential Congress members by Out-Degree. This metric shows members who actively reach out and connect with the most other members.'
};

// ═══════════════════════════════════════════════════════════════════
// 2. GLOBAL VARIABLES FOR DATA
// ═══════════════════════════════════════════════════════════════════

let communityData = {};
let topInfluencers = {};
let degreeDistribution = [];
let heatmapData = {};
let interactionTypes = [];
let temporalData = [];
let networkData = {};
let statsData = {};

// ═══════════════════════════════════════════════════════════════════
// 3. LOAD DATA FROM JSON
// ═══════════════════════════════════════════════════════════════════

async function loadNetworkData() {
    try {
        console.log('📥 Loading JSON data...');
        console.log('🔍 Current URL:', window.location.href);
        
        const possiblePaths = [
            '/portfolio/unit2/checkpoint3/congress_network_data.json',
            '/static/Portfolio/js/checkpoint3/congress_network_data.json',
            './congress_network_data.json',
            'congress_network_data.json'
        ];
        
        let response = null;
        let successfulPath = null;
        
        for (const path of possiblePaths) {
            console.log(`🔄 Trying path: ${path}`);
            try {
                response = await fetch(path);
                if (response.ok) {
                    successfulPath = path;
                    console.log(`✅ Successful path: ${path}`);
                    break;
                }
            } catch (err) {
                console.log(`❌ Failed path: ${path}`);
            }
        }
        
        if (!response || !response.ok) {
            throw new Error(`Could not load JSON from any path`);
        }
        
        const data = await response.json();
        
        communityData = data.communities;
        topInfluencers = data.topInfluencers;
        degreeDistribution = data.degreeDistribution;
        heatmapData = data.heatmap;
        interactionTypes = data.interactionTypes;
        temporalData = data.temporalData;
        networkData = data.network;
        statsData = data.stats;
        
        console.log('✅ Data loaded successfully:');
        console.log(`   • ${statsData.num_nodes} total nodes`);
        console.log(`   • ${statsData.num_edges} total edges`);
        console.log(`   • ${statsData.num_communities} communities`);
        
        return true;
        
    } catch (error) {
        console.error('❌ Error loading data:', error);
        alert('Error loading analysis data. Check that the JSON file is in the correct location.');
        return false;
    }
}

// ═══════════════════════════════════════════════════════════════════
// 4. TOOLTIP SYSTEM
// ═══════════════════════════════════════════════════════════════════

function showTooltip(event, html) {
    const tooltip = d3.select('#tooltip');
    tooltip.html(html);
    tooltip.style('opacity', 1);
    
    const tooltipNode = tooltip.node();
    const tooltipWidth = tooltipNode.offsetWidth;
    const tooltipHeight = tooltipNode.offsetHeight;
    
    let left = event.clientX + 15;
    let top = event.clientY - tooltipHeight - 15;
    
    if (left + tooltipWidth > window.innerWidth) {
        left = event.clientX - tooltipWidth - 15;
    }
    
    if (top < 0) {
        top = event.clientY + 15;
    }
    
    if (top + tooltipHeight > window.innerHeight) {
        top = window.innerHeight - tooltipHeight - 10;
    }
    
    if (left < 0) {
        left = 10;
    }
    
    tooltip
        .style('left', left + 'px')
        .style('top', top + 'px')
        .style('pointer-events', 'none');
}

function hideTooltip() {
    d3.select('#tooltip').style('opacity', 0);
}

// ═══════════════════════════════════════════════════════════════════
// 5. TAB SYSTEM
// ═══════════════════════════════════════════════════════════════════

function changeTab(tabName) {
    const allTabs = document.querySelectorAll('.tab-content');
    allTabs.forEach(tab => tab.classList.remove('active'));
    
    const allButtons = document.querySelectorAll('.tab-button');
    allButtons.forEach(btn => btn.classList.remove('active'));
    
    const selectedTab = document.getElementById(tabName);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    const selectedButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (selectedButton) {
        selectedButton.classList.add('active');
    }
    
    switch(tabName) {
        case 'overview':
            updateOverviewCharts();
            break;
        case 'influencers':
            updateInfluencersCharts();
            break;
        case 'interactions':
            updateInteractionsCharts();
            break;
        case 'communities':
            updateCommunitiesCharts();
            break;
    }
    
    console.log(`✅ Tab changed to: ${tabName}`);
}

// ═══════════════════════════════════════════════════════════════════
// 6. INITIALIZATION FUNCTIONS
// ═══════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 Congress Network Dashboard initializing...');
    
    const dataLoaded = await loadNetworkData();
    
    if (dataLoaded) {
        updateOverviewCharts();
        setupResponsiveResize();
        console.log('✅ Dashboard initialized correctly');
    } else {
        console.error('❌ Could not initialize dashboard');
    }
});

function setupResponsiveResize() {
    let resizeTimer;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            const activeTab = document.querySelector('.tab-content.active');
            if (activeTab) {
                const tabId = activeTab.id;
                changeTab(tabId);
            }
        }, 250);
    });
}

// ═══════════════════════════════════════════════════════════════════
// 7. UPDATE FUNCTIONS BY TAB
// ═══════════════════════════════════════════════════════════════════

function updateOverviewCharts() {
    drawNetworkGraph();
    drawCommunityDistribution();
    drawDegreeDistribution();
}

function updateInfluencersCharts() {
    drawTopInfluencers();
    drawCentralityComparison();
}

function updateInteractionsCharts() {
    drawInteractionTypes();
    drawTemporalEvolution();
}

function updateCommunitiesCharts() {
    drawCommunityAnalysis();
    drawCommunityConnections();
}

// ═══════════════════════════════════════════════════════════════════
// 8. DRAWING FUNCTIONS - OVERVIEW TAB
// ═══════════════════════════════════════════════════════════════════

function drawNetworkGraph() {
    const container = d3.select('#network-graph');
    container.html('');
    
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = container.node().getBoundingClientRect().height;
    
    const svg = container.append('svg')
        .attr('width', containerWidth)
        .attr('height', containerHeight)
        .style('display', 'block');
    
    const nodes = networkData.nodes.map(d => ({...d}));
    const links = networkData.links.map(d => ({...d}));
    
    const sizeScale = d3.scaleLinear()
        .domain([0, d3.max(nodes, d => d.centrality)])
        .range([5, 30]);
    
    const simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(50))
        .force('charge', d3.forceManyBody().strength(-50))
        .force('center', d3.forceCenter(containerWidth / 2, containerHeight / 2));
    
    const link = svg.append('g')
        .selectAll('line')
        .data(links)
        .enter().append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.sqrt(d.value));
    
    const node = svg.append('g')
        .selectAll('circle')
        .data(nodes)
        .enter().append('circle')
        .attr('r', d => sizeScale(d.centrality))
        .attr('fill', d => communityColors[d.group] || '#667eea')
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .style('cursor', 'pointer')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .on('mouseover', function(event, d) {
            d3.select(this)
                .attr('stroke', '#fbbf24')
                .attr('stroke-width', 3);
            
            link.style('stroke-opacity', l => 
                (l.source.id === d.id || l.target.id === d.id) ? 0.8 : 0.1
            )
            .style('stroke', l => 
                (l.source.id === d.id || l.target.id === d.id) ? '#fbbf24' : '#94a3b8'
            )
            .style('stroke-width', l => 
                (l.source.id === d.id || l.target.id === d.id) ? 3 : Math.max(Math.sqrt(l.value), 2)
            );
            
            showTooltip(event, `
                <strong>Member ${d.id}</strong><br/>
                Community: ${d.group}<br/>
                Centrality: ${d.centrality.toFixed(2)}<br/>
                Degree: ${d.degree || 'N/A'}
            `);
        })
        .on('mouseout', function() {
            d3.select(this)
                .attr('stroke', '#fff')
                .attr('stroke-width', 2);
            
            link.style('stroke-opacity', 0.4)
                .style('stroke', '#94a3b8')
                .style('stroke-width', d => Math.max(Math.sqrt(d.value), 2));
            
            hideTooltip();
        });
    
    const label = svg.append('g')
        .selectAll('text')
        .data(nodes.filter(d => d.centrality > 10))
        .enter().append('text')
        .text(d => d.id)
        .attr('font-size', '10px')
        .attr('dx', 12)
        .attr('dy', 4);
    
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
    
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    console.log('✅ Network graph drawn');
}

function drawCommunityDistribution() {
    const container = d3.select('#community-distribution');
    container.html('');
    
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = container.node().getBoundingClientRect().height;
    
    const svg = container.append('svg')
        .attr('width', containerWidth)
        .attr('height', containerHeight)
        .style('display', 'block')
        .append('g')
        .attr('transform', `translate(${containerWidth / 2}, ${containerHeight / 2})`);
    
    const radius = Math.min(containerWidth, containerHeight) / 2 - 40;
    
    const pie = d3.pie()
        .value(d => d.size)
        .sort(null);
    
    const arc = d3.arc()
        .innerRadius(radius * 0.5)
        .outerRadius(radius);
    
    const communities = Object.values(communityData);
    const totalNodes = communities.reduce((sum, c) => sum + c.size, 0);
    
    const arcs = svg.selectAll('arc')
        .data(pie(communities))
        .enter()
        .append('g');
    
    arcs.append('path')
        .attr('d', arc)
        .attr('fill', d => d.data.color)
        .attr('stroke', 'white')
        .attr('stroke-width', 2)
        .attr('opacity', 0.8)
        .on('mouseover', function(event, d) {
            d3.select(this).attr('opacity', 1);
            const percentage = ((d.data.size / totalNodes) * 100).toFixed(1);
            showTooltip(event, `
                <strong>${d.data.label}</strong><br/>
                Members: ${d.data.size}<br/>
                Percentage: ${percentage}%
            `);
        })
        .on('mouseout', function() {
            d3.select(this).attr('opacity', 0.8);
            hideTooltip();
        });
    
    arcs.append('text')
        .attr('transform', d => `translate(${arc.centroid(d)})`)
        .attr('text-anchor', 'middle')
        .attr('font-weight', 'bold')
        .attr('font-size', '12px')
        .attr('fill', 'white')
        .text(d => d.data.label);
    
    console.log('✅ Community distribution drawn');
}

function drawDegreeDistribution() {
    const container = d3.select('#degree-distribution');
    container.html('');
    
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = container.node().getBoundingClientRect().height;
    
    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = containerWidth - margin.left - margin.right;
    const height = containerHeight - margin.top - margin.bottom;
    
    const svg = container.append('svg')
        .attr('width', containerWidth)
        .attr('height', containerHeight)
        .style('display', 'block')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    const x = d3.scaleBand()
        .domain(degreeDistribution.map(d => d.degree))
        .range([0, width])
        .padding(0.1);
    
    const y = d3.scaleLinear()
        .domain([0, d3.max(degreeDistribution, d => d.count)])
        .range([height, 0]);
    
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x));
    
    svg.append('g')
        .attr('class', 'axis')
        .call(d3.axisLeft(y));
    
    svg.selectAll('rect')
        .data(degreeDistribution)
        .enter()
        .append('rect')
        .attr('x', d => x(d.degree))
        .attr('y', d => y(d.count))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.count))
        .attr('fill', '#667eea')
        .attr('opacity', 0.8)
        .on('mouseover', function(event, d) {
            d3.select(this).attr('opacity', 1);
            showTooltip(event, `
                <strong>Degree: ${d.degree}</strong><br/>
                Members: ${d.count}
            `);
        })
        .on('mouseout', function() {
            d3.select(this).attr('opacity', 0.8);
            hideTooltip();
        });
    
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', height + 35)
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .attr('fill', '#666')
        .text('Connection Degree');
    
    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', -45)
        .attr('x', -(height / 2))
        .style('text-anchor', 'middle')
        .style('font-size', '12px')
        .attr('fill', '#666')
        .text('Number of Members');
    
    console.log('✅ Degree distribution drawn');
}

// ═══════════════════════════════════════════════════════════════════
// 9. DRAWING FUNCTIONS - INFLUENCERS TAB
// ═══════════════════════════════════════════════════════════════════

function drawTopInfluencers() {
    const container = d3.select('#top-influencers');
    container.html('');
    
    const metric = document.getElementById('centrality-metric').value;
    const data = topInfluencers[metric];
    
    if (!data || data.length === 0) {
        console.error('No data for metric:', metric);
        return;
    }
    
    const descriptionElement = document.querySelector('#top-influencers').parentElement.querySelector('.description-text');
    if (descriptionElement) {
        descriptionElement.textContent = centralityDescriptions[metric];
    }
    
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = container.node().getBoundingClientRect().height;
    
    const margin = { top: 20, right: 30, bottom: 40, left: 100 };
    const width = containerWidth - margin.left - margin.right;
    const height = containerHeight - margin.top - margin.bottom;
    
    const svg = container.append('svg')
        .attr('width', containerWidth)
        .attr('height', containerHeight)
        .style('display', 'block')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    const x = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.score)])
        .range([0, width]);
    
    const y = d3.scaleBand()
        .domain(data.map(d => d.node))
        .range([0, height])
        .padding(0.2);
    
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x));
    
    svg.append('g')
        .attr('class', 'axis')
        .call(d3.axisLeft(y));
    
    svg.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', 0)
        .attr('y', d => y(d.node))
        .attr('width', d => x(d.score))
        .attr('height', y.bandwidth())
        .attr('fill', d => communityColors[d.community] || '#667eea')
        .attr('opacity', 0.8)
        .attr('rx', 4)
        .on('mouseover', function(event, d) {
            d3.select(this).attr('opacity', 1);
            showTooltip(event, `
                <strong>Member ${d.node}</strong><br/>
                Community: ${d.community}<br/>
                ${metric.toUpperCase()}: ${d.score.toFixed(4)}
            `);
        })
        .on('mouseout', function() {
            d3.select(this).attr('opacity', 0.8);
            hideTooltip();
        });
    
    svg.selectAll('.label')
        .data(data)
        .enter()
        .append('text')
        .attr('x', d => x(d.score) + 5)
        .attr('y', d => y(d.node) + y.bandwidth() / 2)
        .attr('dominant-baseline', 'middle')
        .style('font-size', '11px')
        .style('font-weight', 'bold')
        .attr('fill', '#333')
        .text(d => d.score.toFixed(4));
    
    console.log(`✅ Top influencers by ${metric} drawn`);
}

function drawCentralityComparison() {
    const container = d3.select('#centrality-comparison');
    container.html('');
    
    const metric = document.getElementById('centrality-metric').value;
    const data = topInfluencers[metric];
    
    if (!data || data.length === 0) {
        console.error('No data for metric:', metric);
        return;
    }
    
    const top5Data = data.slice(0, 5);
    
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = container.node().getBoundingClientRect().height;
    
    const margin = { top: 20, right: 30, bottom: 60, left: 100 };
    const width = containerWidth - margin.left - margin.right;
    const height = containerHeight - margin.top - margin.bottom;
    
    const svg = container.append('svg')
        .attr('width', containerWidth)
        .attr('height', containerHeight)
        .style('display', 'block')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    const x = d3.scaleBand()
        .domain(top5Data.map(d => d.node))
        .range([0, width])
        .padding(0.2);
    
    const y = d3.scaleLinear()
        .domain([0, d3.max(top5Data, d => d.score) * 1.1])
        .range([height, 0]);
    
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x));
    
    svg.append('g')
        .attr('class', 'axis')
        .call(d3.axisLeft(y));
    
    svg.selectAll('rect')
        .data(top5Data)
        .enter()
        .append('rect')
        .attr('x', d => x(d.node))
        .attr('y', d => y(d.score))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.score))
        .attr('fill', centralityColors[metric])
        .attr('opacity', 0.8)
        .attr('rx', 4)
        .on('mouseover', function(event, d) {
            d3.select(this).attr('opacity', 1);
            showTooltip(event, `
                <strong>Member ${d.node}</strong><br/>
                Community: ${d.community}<br/>
                ${metric.toUpperCase()}: ${d.score.toFixed(4)}
            `);
        })
        .on('mouseout', function() {
            d3.select(this).attr('opacity', 0.8);
            hideTooltip();
        });
    
    svg.selectAll('.label')
        .data(top5Data)
        .enter()
        .append('text')
        .attr('x', d => x(d.node) + x.bandwidth() / 2)
        .attr('y', d => y(d.score) - 5)
        .attr('text-anchor', 'middle')
        .style('font-size', '11px')
        .style('font-weight', 'bold')
        .attr('fill', '#333')
        .text(d => d.score.toFixed(4));
    
    const legend = svg.append('g')
        .attr('transform', `translate(0,${height + 40})`);
    
    legend.append('rect')
        .attr('x', width / 2 - 60)
        .attr('y', 0)
        .attr('width', 15)
        .attr('height', 15)
        .attr('fill', centralityColors[metric]);
    
    legend.append('text')
        .attr('x', width / 2 - 40)
        .attr('y', 12)
        .style('font-size', '12px')
        .text(metric);
    
    console.log(`✅ Centrality comparison for ${metric} drawn`);
}

// ═══════════════════════════════════════════════════════════════════
// 10. DRAWING FUNCTIONS - INTERACTIONS TAB
// ═══════════════════════════════════════════════════════════════════

function drawInteractionTypes() {
    const container = d3.select('#interaction-types');
    container.html('');
    
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = container.node().getBoundingClientRect().height;
    
    const radius = Math.min(containerWidth, containerHeight) / 2 - 40;
    
    const svg = container.append('svg')
        .attr('width', containerWidth)
        .attr('height', containerHeight)
        .style('display', 'block')
        .append('g')
        .attr('transform', `translate(${containerWidth / 2},${containerHeight / 2})`);
    
    const pie = d3.pie()
        .value(d => d.count)
        .sort(null);
    
    const arc = d3.arc()
        .innerRadius(radius * 0.5)
        .outerRadius(radius);
    
    const color = d3.scaleOrdinal()
        .domain(interactionTypes.map(d => d.type))
        .range(['#667eea', '#f56565', '#48bb78', '#ed8936']);
    
    const arcs = svg.selectAll('arc')
        .data(pie(interactionTypes))
        .enter()
        .append('g');
    
    arcs.append('path')
        .attr('d', arc)
        .attr('fill', d => color(d.data.type))
        .attr('stroke', 'white')
        .attr('stroke-width', 2)
        .attr('opacity', 0.8)
        .on('mouseover', function(event, d) {
            d3.select(this).attr('opacity', 1);
            showTooltip(event, `
                <strong>${d.data.type}</strong><br/>
                Count: ${d.data.count}<br/>
                Percentage: ${d.data.percentage}%
            `);
        })
        .on('mouseout', function() {
            d3.select(this).attr('opacity', 0.8);
            hideTooltip();
        });
    
    arcs.append('text')
        .attr('transform', d => `translate(${arc.centroid(d)})`)
        .attr('text-anchor', 'middle')
        .attr('font-weight', 'bold')
        .attr('font-size', '11px')
        .attr('fill', 'white')
        .text(d => d.data.type);
    
    console.log('✅ Interaction types drawn');
}

function drawTemporalEvolution() {
    const container = d3.select('#temporal-evolution');
    container.html('');
    
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = container.node().getBoundingClientRect().height;
    
    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = containerWidth - margin.left - margin.right;
    const height = containerHeight - margin.top - margin.bottom;
    
    const svg = container.append('svg')
        .attr('width', containerWidth)
        .attr('height', containerHeight)
        .style('display', 'block')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    const dataWithDates = temporalData.map(d => ({
        date: new Date(d.date),
        interactions: d.interactions
    }));
    
    const x = d3.scaleTime()
        .domain(d3.extent(dataWithDates, d => d.date))
        .range([0, width]);
    
    const y = d3.scaleLinear()
        .domain([0, d3.max(dataWithDates, d => d.interactions)])
        .range([height, 0]);
    
    const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.interactions))
        .curve(d3.curveMonotoneX);
    
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(5));
    
    svg.append('g')
        .attr('class', 'axis')
        .call(d3.axisLeft(y));
    
    svg.append('path')
        .datum(dataWithDates)
        .attr('fill', 'none')
        .attr('stroke', '#667eea')
        .attr('stroke-width', 2.5)
        .attr('d', line);
    
    svg.selectAll('circle')
        .data(dataWithDates)
        .enter()
        .append('circle')
        .attr('cx', d => x(d.date))
        .attr('cy', d => y(d.interactions))
        .attr('r', 3)
        .attr('fill', '#667eea')
        .attr('opacity', 0.6)
        .on('mouseover', function(event, d) {
            d3.select(this).attr('r', 6).attr('opacity', 1);
            showTooltip(event, `
                <strong>${d.date.toLocaleDateString()}</strong><br/>
                Interactions: ${d.interactions}
            `);
        })
        .on('mouseout', function() {
            d3.select(this).attr('r', 3).attr('opacity', 0.6);
            hideTooltip();
        });
    
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', height + 35)
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .attr('fill', '#666')
        .text('Date');
    
    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', -45)
        .attr('x', -(height / 2))
        .style('text-anchor', 'middle')
        .style('font-size', '12px')
        .attr('fill', '#666')
        .text('Interactions');
    
    console.log('✅ Temporal evolution drawn');
}

// ═══════════════════════════════════════════════════════════════════
// 11. DRAWING FUNCTIONS - COMMUNITIES TAB
// ═══════════════════════════════════════════════════════════════════

function drawCommunityAnalysis() {
    const container = d3.select('#community-analysis');
    container.html('');
    
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = container.node().getBoundingClientRect().height;
    
    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = containerWidth - margin.left - margin.right;
    const height = containerHeight - margin.top - margin.bottom;
    
    const svg = container.append('svg')
        .attr('width', containerWidth)
        .attr('height', containerHeight)
        .style('display', 'block')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    const communities = Object.values(communityData);
    
    const x = d3.scaleBand()
        .domain(communities.map(d => d.label))
        .range([0, width])
        .padding(0.2);
    
    const y = d3.scaleLinear()
        .domain([0, d3.max(communities, d => d.size)])
        .range([height, 0]);
    
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x));
    
    svg.append('g')
        .attr('class', 'axis')
        .call(d3.axisLeft(y));
    
    svg.selectAll('rect')
        .data(communities)
        .enter()
        .append('rect')
        .attr('x', d => x(d.label))
        .attr('y', d => y(d.size))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.size))
        .attr('fill', d => d.color)
        .attr('opacity', 0.8)
        .on('mouseover', function(event, d) {
            d3.select(this).attr('opacity', 1);
            const totalNodes = communities.reduce((sum, c) => sum + c.size, 0);
            const percentage = ((d.size / totalNodes) * 100).toFixed(1);
            showTooltip(event, `
                <strong>${d.label}</strong><br/>
                Members: ${d.size}<br/>
                Percentage: ${percentage}%
            `);
        })
        .on('mouseout', function() {
            d3.select(this).attr('opacity', 0.8);
            hideTooltip();
        });
    
    svg.selectAll('.label')
        .data(communities)
        .enter()
        .append('text')
        .attr('x', d => x(d.label) + x.bandwidth() / 2)
        .attr('y', d => y(d.size) - 5)
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .style('font-weight', 'bold')
        .attr('fill', '#333')
        .text(d => d.size);
    
    console.log('✅ Community analysis drawn');
}

function drawCommunityConnections() {
    const container = d3.select('#community-connections');
    container.html('');
    
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = container.node().getBoundingClientRect().height;
    
    const svg = container.append('svg')
        .attr('width', containerWidth)
        .attr('height', containerHeight)
        .style('display', 'block');
    
    const communities = Object.values(communityData);
    const connections = [];
    
    for (let i = 0; i < communities.length; i++) {
        for (let j = i + 1; j < communities.length; j++) {
            connections.push({
                source: communities[i].label,
                target: communities[j].label,
                value: Math.floor(Math.random() * 50) + 10
            });
        }
    }
    
    const communityNodes = communities.map(d => ({
        id: d.label,
        size: d.size,
        color: d.color
    }));
    
    const simulation = d3.forceSimulation(communityNodes)
        .force('link', d3.forceLink(connections).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-100))
        .force('center', d3.forceCenter(containerWidth / 2, containerHeight / 2));
    
    const link = svg.append('g')
        .selectAll('line')
        .data(connections)
        .enter().append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6)
        .attr('stroke-width', d => Math.sqrt(d.value));
    
    const node = svg.append('g')
        .selectAll('circle')
        .data(communityNodes)
        .enter().append('circle')
        .attr('r', d => Math.sqrt(d.size) * 2)
        .attr('fill', d => d.color)
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended))
        .on('mouseover', function(event, d) {
            const totalNodes = communities.reduce((sum, c) => sum + c.size, 0);
            showTooltip(event, `
                <strong>${d.id}</strong><br/>
                Members: ${d.size}<br/>
                Percentage: ${((d.size / totalNodes) * 100).toFixed(1)}%
            `);
        })
        .on('mouseout', hideTooltip);
    
    const label = svg.append('g')
        .selectAll('text')
        .data(communityNodes)
        .enter().append('text')
        .text(d => d.id)
        .attr('font-size', '14px')
        .attr('font-weight', 'bold')
        .attr('dx', 15)
        .attr('dy', 4);
    
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);
        
        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);
        
        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });
    
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    console.log('✅ Community connections drawn');
}

// ═══════════════════════════════════════════════════════════════════
// 12. AUXILIARY FUNCTIONS
// ═══════════════════════════════════════════════════════════════════

function updateCentralityMetric() {
    drawTopInfluencers();
    drawCentralityComparison();
}

function downloadData(format) {
    const data = {
        stats: statsData,
        communities: communityData,
        influencers: topInfluencers,
        interactions: interactionTypes,
        temporal: temporalData,
        degree: degreeDistribution,
        network: {
            nodes: networkData.nodes.length,
            links: networkData.links.length
        }
    };
    
    let content, mimeType, extension;
    
    if (format === 'json') {
        content = JSON.stringify(data, null, 2);
        mimeType = 'application/json';
        extension = 'json';
    } else {
        let csvContent = 'Metric,Value\n';
        csvContent += `Total Nodes,${statsData.num_nodes}\n`;
        csvContent += `Total Edges,${statsData.num_edges}\n`;
        csvContent += `Modularity,${statsData.modularity}\n`;
        csvContent += `Communities,${statsData.num_communities}\n`;
        csvContent += `Density,${statsData.density}\n`;
        csvContent += `Avg Clustering,${statsData.avg_clustering}\n`;
        
        content = csvContent;
        mimeType = 'text/csv';
        extension = 'csv';
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `congress_network_analysis.${extension}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    console.log(`✅ Data downloaded in ${format} format`);
}

// ═══════════════════════════════════════════════════════════════════
// 13. INITIALIZATION LOG
// ═══════════════════════════════════════════════════════════════════

console.log('📊 Congress Network Analysis Dashboard loaded');
console.log('🔄 Waiting for data load from JSON...');