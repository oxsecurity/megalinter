/**
 * L.Control.GeoSearch - search for an address and zoom to it's location
 * L.GeoSearch.Provider.OpenStreetMap uses openstreetmap geocoding service
 * https://github.com/smeijer/L.GeoSearch
 */

L.GeoSearch.Provider.OpenStreetMap = L.Class.extend({
    options: {},

    initialize: function(options) {
        options = L.Util.setOptions(this, options);
    },

    GetServiceUrl: function (qry) {
        var parameters = L.Util.extend({
            q: qry,
            format: 'json'
        }, this.options);

        return (location.protocol === 'https:' ? 'https:' : 'http:')
            + '//nominatim.openstreetmap.org/search'
            + L.Util.getParamString(parameters);
    },

    ParseJSON: function (data) {
        var results = [];

        for (var i = 0; i < data.length; i++) {
            var boundingBox = data[i].boundingbox,
                northEastLatLng = new L.LatLng( boundingBox[1], boundingBox[3] ),
                southWestLatLng = new L.LatLng( boundingBox[0], boundingBox[2] );

            if (data[i].address)
                data[i].address.type = data[i].type;

            results.push(new L.GeoSearch.Result(
                data[i].lon,
                data[i].lat,
                data[i].display_name,
                new L.LatLngBounds([
                    northEastLatLng,
                    southWestLatLng
                ]),
                data[i].address
            ));
        }

        return results;
    }
});
