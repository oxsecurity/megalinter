
# Leaflet-providers changelog

## 1.1.17 (2017-06-29)
 - Added `maxZoom` for `Hydda` provider [242](https://github.com/leaflet-extras/leaflet-providers/pull/242)
 - Fixed `maxZoom` for all layers from the `thunderforest` provider
 - Added protocol relativity to the url for `OpenStreetMap.DE` variant.
 - Added `OpenStreetMap.BZH` [#255](https://github.com/leaflet-extras/leaflet-providers/pull/255)
 - Added `nlmaps` provider [#254](https://github.com/leaflet-extras/leaflet-providers/pull/254)

## 1.1.16 (2016-11-04)
 - Updates to reflect changes in [BasemapAT](http://leaflet-extras.github.io/leaflet-providers/preview/#filter=BasemapAT) by [@ximex](https://github.com/ximex), [#232]((https://github.com/leaflet-extras/leaflet-providers/pull/232), [#233]((https://github.com/leaflet-extras/leaflet-providers/pull/233)
 - Bump leaflet version in tests and preview to 1.0.1.
 - Added some layers from http://justicemap.org [#224](https://github.com/leaflet-extras/leaflet-providers/pull/224).

## 1.1.15 (2016-08-09)
 - [Stamen terrain](http://leaflet-extras.github.io/leaflet-providers/preview/#filter=Stamen.Terrain) now has world coverage [#223](https://github.com/leaflet-extras/leaflet-providers/pull/223)
 - OSM France `maxZoom`: 20 ([#222](https://github.com/leaflet-extras/leaflet-providers/pull/222), fixes [#221](https://github.com/leaflet-extras/leaflet-providers/issues/221))

## 1.1.14 (2016-07-15)
 - Remove MapQuest, fixes #219
 - Accidently skipped v1.1.12 and v1.1.13

## 1.1.11 (2016-06-04)
 - Added protocol relativity to OSM FR, OSM HOT and Hydda providers (#214, #215).

## 1.1.9 (2016-03-23)
 - Re-added HERE layers #209, discussion in #206.

## 1.1.8 (2016-03-22)
 - Removed HERE layers #206

## 1.1.7 (2015-12-16)
 - Removed Acetate tile layers #198

## 1.1.6 (2015-11-03)
 - Removed most of the NLS layers per NLS request #193, fixes #178
 - Added new variants to the HERE provider #183 by [@andreaswc](https://github.com/andreaswc)
 - Added some tests to make sure all the placeholders in the url template are replaced #188

## 1.1.5 (2015-10-01)
 - Improvements for the NLS layers #182 by [@tomhughes](https://github.com/tomhughes)
 - Check for valid bounds before fitting the preview map to undefined (fixes #185)
 - Add bounds for FreeMapSK (fixes #184)
 - Fix Stamen layers with `.jpg` extension (#187, fixes #184)

## 1.1.4 (2015-09-27)
 - Only include the interesting files in the npm package #180
 - Add GSGS_Ireland to NLS provider with `tms:true` to invert y-axis #181

## 1.1.3 (2015-09-26)
 - Add various historical layers of the Natioanal library of Scotland (NLS) #179
 - Add a page to visually check bounds #179

## 1.1.2 (2015-09-05)
 - Add CartoDB labels-only styles #170 by [@almccon](https://github.com/almccon)
 - Implement commonjs module #172
 - Added retina URL option #177, [@routexl](https://github.com/routexl)

## 1.1.1 (2015-06-22)
 - Update Mapbox API to v4 #167 by [@gutenye](https://github.com/gutenye)
 - Started maintaining a changelog in CHANGELOG.md.
