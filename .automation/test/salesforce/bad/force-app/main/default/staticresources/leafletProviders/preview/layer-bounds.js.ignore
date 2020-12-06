var table = L.DomUtil.get('table');
var container = L.DomUtil.get('maps');
var result = L.DomUtil.get('result');

var map, rect;

function showBounds () {
	if (!(map && result)) {
		return;
	}
	var b = rect.getBounds()
	result.innerHTML = '<h2> Bounds for this layer:</h2>' +
		'<code>\n\n[' +
		'[' + b.getSouth() + ', ' + b.getWest() + '], ' +
		'[' + b.getNorth() + ', ' + b.getEast() + ']' +
		']</code><br /><br />' +
		'zoomlevel: ' + map.getZoom();
}

function addLayer (provider) {
	var layer = L.tileLayer.provider(provider);

	// we're only interested in layers with bounds here.
	if (!layer.options.bounds) {
		return;
	}
	var bounds = L.latLngBounds(layer.options.bounds);

	var row = L.DomUtil.create('tr', '', table);
	L.DomUtil.create('td', '', row).innerHTML = provider;

	L.DomEvent.on(row, 'click', function () {
		if (map && map.remove) {
			map.remove();
		}
		for (var i = 0; i < table.children.length; i++) {
			L.DomUtil.removeClass(table.children[i], 'active');
		}
		L.DomUtil.addClass(row, 'active');

		container.innerHTML = '';
		L.DomUtil.create('h2', '', container).innerHTML = provider;

		map = L.map(L.DomUtil.create('div', 'map', container)).setView([52, 4], 6);
		map.addLayer(L.tileLayer.provider('Hydda.Base'));
		map.addLayer(layer);

		rect = L.rectangle(bounds, {
			fill: false,
			weight: 2,
			opacity: 1
		}).addTo(map);

		rect.editing.enable();
		map.on('click zoomend', showBounds);
		showBounds();

		map.fitBounds(bounds);
	});
}
L.DomEvent.on(L.DomUtil.get('dump-bounds'), 'click', showBounds);

L.tileLayer.provider.eachLayer(addLayer);
