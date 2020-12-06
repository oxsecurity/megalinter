#Leaflet.GeoSearch
Adds support for geocoding (address lookup, a.k.a. geoseaching) to [Leaflet](leafletjs.com).

Check out the [demo](http://smeijer.github.io/L.GeoSearch)

#About the control
The control uses so-called "providers" to take care of building the correct service URL and parsing
the retrieved data into a uniform format. Thanks to this architecture, it is pretty easy to write
your own providers, so you can use your own geocoding service(s).

The control comes with a default set of three providers:

  - L.GeoSearch.Provider.Esri
  - L.GeoSearch.Provider.Google
  - L.GeoSearch.Provider.OpenStreetMap

Using these is pretty simple.

#Using the control

For example, to use the Esri provider:

````javascript
new L.Control.GeoSearch({
    provider: new L.GeoSearch.Provider.Esri()
}).addTo(map);
````

Or if you prefer using Google

````javascript
new L.Control.GeoSearch({
    provider: new L.GeoSearch.Provider.Google()
}).addTo(map);
````

Or, for open-source lovers who like OpenStreetMap:

````javascript
new L.Control.GeoSearch({
    provider: new L.GeoSearch.Provider.OpenStreetMap()
}).addTo(map);
````

I really can't make it any harder. Checkout the providers to see how easy it is to write your own.
There are other configurable options like setting the position of the search input and whether or not a marker should be displayed at the position of the search result.

````javascript
new L.Control.GeoSearch({
    provider: new L.GeoSearch.Provider.OpenStreetMap(),
    position: 'topleft',
    showMarker: true,
    retainZoomLevel: false,
}).addTo(map);
````

If you want to have your custom GeoSearch control you can directly use one of the providers. 

````javascript
var googleGeocodeProvider = new L.GeoSearch.Provider.Google(),
  addressText = 'Amsterdam';

googleGeocodeProvider.GetLocations( addressText, function ( data ) {
  // in data are your results with x, y, label and bounds (currently availabel for google maps provider only)
});

````

I really can't make it any easier. Check out the providers to see how easy it is to write your own.
