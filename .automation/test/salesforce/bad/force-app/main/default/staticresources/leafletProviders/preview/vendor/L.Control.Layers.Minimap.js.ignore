(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
/*
 * Leaflet.layerscontrol-minimap
 *
 * Layers control with synced minimaps for Leaflet.
 *
 * Jan Pieter Waagmeester <jieter@jieter.nl>
 */
var cloneLayer = require('leaflet-clonelayer');

require('leaflet.sync');

L.Control.Layers.Minimap = L.Control.Layers.extend({
    options: {
        position: 'topright',
        topPadding: 10,
        bottomPadding: 40,
        overlayBackgroundLayer: L.tileLayer('http://{s}.tile.openstreetmap.se/hydda/base/{z}/{x}/{y}.png', {
            attribution: 'Tiles courtesy of <a href="http://openstreetmap.se/" target="_blank">OpenStreetMap Sweden</a> &mdash; ' +
            'Map data &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        })
    },

    filter: function (string) {
        string = string.trim();

        var visibleLayers = {};
        var layerLabels = this._container.querySelectorAll('label');
        for (var i = 0; i < layerLabels.length; i++) {
            var layerLabel = layerLabels[i];

            if (string !== '' && layerLabel._layerName.indexOf(string) === -1) {
                L.DomUtil.addClass(layerLabel, 'leaflet-minimap-hidden');
            } else {
                L.DomUtil.removeClass(layerLabel, 'leaflet-minimap-hidden');
                visibleLayers[layerLabel._layerName] = cloneLayer(layerLabel._minimap._layer);
            }
        }
        this._onListScroll();

        return visibleLayers;
    },

    isCollapsed: function () {
        return !L.DomUtil.hasClass(this._container, 'leaflet-control-layers-expanded');
    },

    _expand: function () {
        L.Control.Layers.prototype._expand.call(this);
        this._onListScroll();
    },

    _initLayout: function () {
        L.Control.Layers.prototype._initLayout.call(this);
        var container = this._container;

        L.DomUtil.addClass(container, 'leaflet-control-layers-minimap');
        L.DomEvent.on(container, 'scroll', this._onListScroll, this);
        // disable scroll propagation, Leaflet is going to do this too
        // https://github.com/Leaflet/Leaflet/issues/5277
        L.DomEvent.disableScrollPropagation(container)
    },

    _update: function () {
        L.Control.Layers.prototype._update.call(this);

        this._map.on('resize', this._onResize, this);
        this._onResize();
        this._map.whenReady(this._onListScroll, this);
    },

    _addItem: function (obj) {
        var container = obj.overlay ? this._overlaysList : this._baseLayersList;
        var label = L.DomUtil.create('label', 'leaflet-minimap-container', container);
        label._layerName = obj.name;
        var checked = this._map.hasLayer(obj.layer);

        label._minimap = this._createMinimap(
            L.DomUtil.create('div', 'leaflet-minimap', label),
            obj.layer,
            obj.overlay
        );
        var span = L.DomUtil.create('span', 'leaflet-minimap-label', label);

        var input;
        if (obj.overlay) {
            input = document.createElement('input');
            input.type = 'checkbox';
            input.className = 'leaflet-control-layers-selector';
            input.defaultChecked = checked;
        } else {
            input = this._createRadioElement('leaflet-base-layers', checked);
        }
        input.layerId = L.stamp(obj.layer);
        span.appendChild(input);

        L.DomEvent.on(label, 'click', this._onInputClick, this);

        var name = L.DomUtil.create('span', '', span);
        name.innerHTML = ' ' + obj.name;

        return label;
    },

    _onResize: function () {
        var mapHeight = this._map.getContainer().clientHeight;
        var controlHeight = this._container.clientHeight;

        if (controlHeight > mapHeight - this.options.bottomPadding) {
            this._container.style.overflowY = 'scroll';
        }
        this._container.style.maxHeight = (mapHeight - this.options.bottomPadding - this.options.topPadding) + 'px';
    },

    _onListScroll: function () {
        if (!this._map) {
            return;
        }

        var minimaps = this._map._container.querySelectorAll('label[class="leaflet-minimap-container"]');
        if (minimaps.length === 0) {
            return;
        }

        // compute indexes of first and last minimap in view
        var first, last;
        if (this.isCollapsed()) {
            first = last = -1;
        } else {
            var minimapHeight = minimaps.item(0).clientHeight;
            var container = this._container;
            var scrollTop = container.scrollTop;

            first = Math.floor(scrollTop / minimapHeight);
            last = Math.ceil((scrollTop + container.clientHeight) / minimapHeight);
        }

        for (var i = 0; i < minimaps.length; ++i) {
            var minimap = minimaps[i].childNodes.item(0);
            var map = minimap._miniMap;
            var layer = map._layer;

            if (!layer) {
                continue;
            }

            if (i >= first && i <= last) {
                if (!map.hasLayer(layer)) {
                    layer.addTo(map);
                }
                map.invalidateSize();
            } else if (map.hasLayer(layer)) {
                map.removeLayer(layer);
            }
        }
    },

    _createMinimap: function (mapContainer, originalLayer, isOverlay) {
        var minimap = mapContainer._miniMap = L.map(mapContainer, {
            attributionControl: false,
            zoomControl: false,
            scrollWheelZoom: false
        });

        // disable minimap interaction.
        minimap.dragging.disable();
        minimap.touchZoom.disable();
        minimap.doubleClickZoom.disable();
        minimap.scrollWheelZoom.disable();

        // create tilelayer, but do not add it to the map yet
        // (only after it's scrolled into view).
        if (isOverlay && this.options.overlayBackgroundLayer) {
            // add a background for overlays if a background layer is defined.
            minimap._layer = L.layerGroup([
                cloneLayer(this.options.overlayBackgroundLayer),
                cloneLayer(originalLayer)
            ]);
        } else {
            minimap._layer = cloneLayer(originalLayer);
        }

        var map = this._map;
        map.whenReady(function () {
            minimap.setView(map.getCenter(), map.getZoom());
            map.sync(minimap);
        });

        return minimap;
    }
});

L.control.layers.minimap = function (baseLayers, overlays, options) {
    return new L.Control.Layers.Minimap(baseLayers, overlays, options);
};

},{"leaflet-clonelayer":2,"leaflet.sync":3}],2:[function(require,module,exports){
function cloneOptions (options) {
    var ret = {};
    for (var i in options) {
        var item = options[i];
        if (item && item.clone) {
            ret[i] = item.clone();
        } else if (item instanceof L.Layer) {
            ret[i] = cloneLayer(item);
        } else {
            ret[i] = item;
        }
    }
    return ret;
}

function cloneInnerLayers (layer) {
    var layers = [];
    layer.eachLayer(function (inner) {
        layers.push(cloneLayer(inner));
    });
    return layers;
}

function cloneLayer (layer) {
    var options = cloneOptions(layer.options);

    // we need to test for the most specific class first, i.e.
    // Circle before CircleMarker

    // Renderers
    if (layer instanceof L.SVG) {
        return L.svg(options);
    }
    if (layer instanceof L.Canvas) {
        return L.canvas(options);
    }

    // Tile layers
    if (layer instanceof L.TileLayer) {
        return L.tileLayer(layer._url, options);
    }
    if (layer instanceof L.ImageOverlay) {
        return L.imageOverlay(layer._url, layer._bounds, options);
    }

    // Marker layers
    if (layer instanceof L.Marker) {
        return L.marker(layer.getLatLng(), options);
    }

    if (layer instanceof L.Circle) {
        return L.circle(layer.getLatLng(), layer.getRadius(), options);
    }
    if (layer instanceof L.CircleMarker) {
        return L.circleMarker(layer.getLatLng(), options);
    }

    if (layer instanceof L.Rectangle) {
        return L.rectangle(layer.getBounds(), options);
    }
    if (layer instanceof L.Polygon) {
        return L.polygon(layer.getLatLngs(), options);
    }
    if (layer instanceof L.Polyline) {
        return L.polyline(layer.getLatLngs(), options);
    }

    if (layer instanceof L.GeoJSON) {
        return L.geoJson(layer.toGeoJSON(), options);
    }

    if (layer instanceof L.LayerGroup) {
        return L.layerGroup(cloneInnerLayers(layer));
    }
    if (layer instanceof L.FeatureGroup) {
        return L.FeatureGroup(cloneInnerLayers(layer));
    }

    throw 'Unknown layer, cannot clone this layer. Leaflet-version: ' + L.version;
}

if (typeof exports === 'object') {
    module.exports = cloneLayer;
}

},{}],3:[function(require,module,exports){
/*
 * Extends L.Map to synchronize the interaction on one map to one or more other maps.
 */

(function () {
    var NO_ANIMATION = {
        animate: false,
        reset: true
    };

    L.Map = L.Map.extend({
        sync: function (map, options) {
            this._initSync();
            options = L.extend({
                noInitialSync: false,
                syncCursor: false,
                syncCursorMarkerOptions: {
                    radius: 10,
                    fillOpacity: 0.3,
                    color: '#da291c',
                    fillColor: '#fff'
                }
            }, options);

            // prevent double-syncing the map:
            if (this._syncMaps.indexOf(map) === -1) {
                this._syncMaps.push(map);
            }

            if (!options.noInitialSync) {
                map.setView(this.getCenter(), this.getZoom(), NO_ANIMATION);
            }
            if (options.syncCursor) {
                map.cursor = L.circleMarker([0, 0], options.syncCursorMarkerOptions).addTo(map);

                this._cursors.push(map.cursor);

                this.on('mousemove', this._cursorSyncMove, this);
                this.on('mouseout', this._cursorSyncOut, this);
            }
            return this;
        },

        _cursorSyncMove: function (e) {
            this._cursors.forEach(function (cursor) {
                cursor.setLatLng(e.latlng);
            });
        },

        _cursorSyncOut: function (e) {
            this._cursors.forEach(function (cursor) {
                // TODO: hide cursor in stead of moving to 0, 0
                cursor.setLatLng([0, 0]);
            });
        },


        // unsync maps from each other
        unsync: function (map) {
            var self = this;

            if (this._syncMaps) {
                this._syncMaps.forEach(function (synced, id) {
                    if (map === synced) {
                        self._syncMaps.splice(id, 1);
                        if (map.cursor) {
                            map.cursor.removeFrom(map);
                        }
                    }
                });
            }
            this.off('mousemove', this._cursorSyncMove, this);
            this.off('mouseout', this._cursorSyncOut, this);

            return this;
        },

        // Checks if the maps is synced with anything
        isSynced: function () {
            return (this.hasOwnProperty('_syncMaps') && Object.keys(this._syncMaps).length > 0);
        },

        // overload methods on originalMap to replay interactions on _syncMaps;
        _initSync: function () {
            if (this._syncMaps) {
                return;
            }
            var originalMap = this;

            this._syncMaps = [];
            this._cursors = [];

            L.extend(originalMap, {
                setView: function (center, zoom, options, sync) {
                    if (!sync) {
                        originalMap._syncMaps.forEach(function (toSync) {
                            toSync.setView(center, zoom, options, true);
                        });
                    }
                    return L.Map.prototype.setView.call(this, center, zoom, options);
                },

                panBy: function (offset, options, sync) {
                    if (!sync) {
                        originalMap._syncMaps.forEach(function (toSync) {
                            toSync.panBy(offset, options, true);
                        });
                    }
                    return L.Map.prototype.panBy.call(this, offset, options);
                },

                _onResize: function (event, sync) {
                    if (!sync) {
                        originalMap._syncMaps.forEach(function (toSync) {
                            toSync._onResize(event, true);
                        });
                    }
                    return L.Map.prototype._onResize.call(this, event);
                }
            });

            originalMap.on('zoomend', function () {
                originalMap._syncMaps.forEach(function (toSync) {
                    toSync.setView(originalMap.getCenter(), originalMap.getZoom(), NO_ANIMATION);
                });
            }, this);

            originalMap.dragging._draggable._updatePosition = function () {
                L.Draggable.prototype._updatePosition.call(this);
                var self = this;
                originalMap._syncMaps.forEach(function (toSync) {
                    L.DomUtil.setPosition(toSync.dragging._draggable._element, self._newPos);
                    toSync.eachLayer(function (layer) {
                        if (layer._google !== undefined) {
                            layer._google.setCenter(originalMap.getCenter());
                        }
                    });
                    toSync.fire('moveend');
                });
            };
        }
    });
})();

},{}]},{},[1]);
