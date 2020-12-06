/**
 * L.Control.GeoSearch - search for an address and zoom to it's location
 * L.GeoSearch.Provider.Google uses google geocoding service
 * https://github.com/smeijer/L.GeoSearch
 */

onLoadGoogleApiCallback = function() {
    L.GeoSearch.Provider.Google.Geocoder = new google.maps.Geocoder();
    var scriptNode = document.getElementById('load_google_api');
    if (!!scriptNode) {
        document.body.removeChild(scriptNode);
    }
};

L.GeoSearch.Provider.Google = L.Class.extend({
    _isReady: false,
    _onReadyQueue: [],

    options: {

    },

    initialize: function(options) {
        options = L.Util.setOptions(this, options);
        if (!window.google || !window.google.maps) {
            this.loadMapsApi();
        } else {
            // if google is already loaded, make sure we initialize the Geocoder
            onLoadGoogleApiCallback();
        }

    },

    loadMapsApi: function () {
        var key = (typeof(this.options.key) !== 'undefined')? this.options.key : "YOUR_API_KEY";
        var self = this;
        var url = "https://maps.googleapis.com/maps/api/js?key="+key+"&v=3&callback=onLoadGoogleApiCallback&sensor=false";
        var script = document.createElement('script');
        script.id = 'load_google_api';
        script.type = "text/javascript";
        script.src = url;
        document.body.appendChild(script);

        var handle = setInterval(function() {
            if (typeof google !== 'undefined' && L.GeoSearch.Provider.Google.Geocoder instanceof google.maps.Geocoder) {
                clearInterval(handle);
                self._onReady();
            }
        }, 25);
    },

    _onReady: function() {
        this._isReady = true;

        var data;
        while (data = this._onReadyQueue.shift()) {
            this.GetLocations(data.qry, data.callback);
        }
    },

    GetLocations: function(qry, callback) {
        if (!this._isReady) {
            // store calls to this method, so the can be re-invoked once
            // the google api is loaded
            this._onReadyQueue.push({ qry: qry, callback: callback });
            return;
        }

        var geocoder = L.GeoSearch.Provider.Google.Geocoder;

        var parameters = L.Util.extend({
            address: qry
        }, this.options);

        var results = geocoder.geocode(parameters, function(data){
            data = {results: data};

            var results = [],
                northEastLatLng,
                southWestLatLng,
                bounds;
            for (var i = 0; i < data.results.length; i++) {

                if( data.results[i].geometry.bounds ) {
                    var northEastGoogle = data.results[i].geometry.bounds.getNorthEast(),
                        southWestGoogle = data.results[i].geometry.bounds.getSouthWest();

                    northEastLatLng = new L.LatLng( northEastGoogle.lat(), northEastGoogle.lng() );
                    southWestLatLng = new L.LatLng( southWestGoogle.lat(), southWestGoogle.lng() );
                    bounds = new L.LatLngBounds([ northEastLatLng, southWestLatLng ]);
                }
                else {
                    bounds = undefined;
                }
                results.push(new L.GeoSearch.Result(
                    data.results[i].geometry.location.lng(),
                    data.results[i].geometry.location.lat(),
                    data.results[i].formatted_address,
                    bounds
                ));
            }

            if(typeof callback == 'function')
                callback(results);
        });
    },
});
