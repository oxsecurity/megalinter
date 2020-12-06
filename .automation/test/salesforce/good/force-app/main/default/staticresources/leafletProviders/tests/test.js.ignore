/* global describe, chai, it */

function isEmpty (obj) {
	for (var prop in obj) {
		if (obj.hasOwnProperty(prop)) {
			return false;
		}
	}

	return true;
}

// List of valid L.TileLayer options to check options against
var validTileLayerOptions = [
	'minZoom', 'minNativeZoom', 'maxZoom', 'maxNativeZoom', 'tileSize',
	'subdomains', 'errorTileUrl', 'attribution', 'tms', 'continuousWorld',
	'noWrap', 'zoomOffset', 'zoomReverse',
	'opacity', 'zIndex', 'unloadInvisibleTiles', 'updateWhenIdle',
	'detectRetina', 'reuseTiles', 'bounds', 'crossOrigin',
	'updateInterval', 'pane', 'nonBubblingEvents', 'updateWhenZooming',
	'className', 'keepBuffer'
];

// monkey-patch getTileUrl with fake values.
L.TileLayer.prototype.getTileUrl = function (coords) {
	return L.Util.template(this._url, L.extend({
		r: '',
		s: this._getSubdomain(coords),
		x: coords.x,
		y: coords.y,
		z: 15
	}, this.options));
};

describe('leaflet-providers', function () {
	chai.should();
	var providers = L.TileLayer.Provider.providers;

	describe('variant definition structure', function () {
		it('each provider has keys url, options, variants', function () {
			for (var name in providers) {
				providers[name].should.contain.any.keys('url', 'options', 'variants');
			}
		});
		it('each variant should be an object or a string', function () {
			for (var name in providers) {
				var variants = providers[name].variants;

				for (var v in variants) {
					if (typeof variants[v] === 'string' || isEmpty(variants[v])) {
						// string or empty object, which is fine.
						continue;
					} else {
						variants[v].should.be.an.instanceof(Object);
						variants[v].should.contain.any.keys('url', 'options');
					}
				}
			}
		});
	});

	describe('Nonexistant providers', function () {
		it('should fail for non-existant providers', function () {
			var fn = function () {
				L.tileLayer.provider('Example');
			};
			fn.should.throw('No such provider (Example)');
		});
		it('should fail for non-existant variants of existing providers', function () {
			var fn = function () {
				L.tileLayer.provider('OpenStreetMap.Example');
			};
			fn.should.throw('No such variant of OpenStreetMap (Example)');
		});
	});

	describe('Each layer', function () {
		L.tileLayer.provider.eachLayer(function (name) {
			describe(name, function () {
				var layer = L.tileLayer.provider(name);

				it('should be a L.TileLayer', function () {
					layer.should.be.an.instanceof(L.TileLayer);
				});

				it('should not throw while requesting a tile url', function () {
					layer.getTileUrl({x: 16369, y: 10896});
				});

				it('should have valid options', function () {
					for (var key in layer.options) {
						if (validTileLayerOptions.indexOf(key) !== -1) {
							continue;
						}
						var placeholder = '{' + key + '}';
						layer._url.should.contain(placeholder);
					}
				})
			});
		});
	})
});
