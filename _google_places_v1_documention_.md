<!-- SECURITY WARNING: NEVER store API keys or credentials in documentation or code files -->
<!-- Always use environment variables or secure credential management systems -->

\<google\_api\_key\>[YOUR\_API\_KEY\_GOES\_HERE]\</google\_api\_key\>  
\<mongo\_uri\>[YOUR\_MONGO\_URI\_GOES\_HERE]\</mongo\_uri\>

\<google\_places\_v1\_documention\>  
Text Search (New) 

bookmark\_border  
Select platform: Android iOS JavaScript Web Service  
A Text Search (New) returns information about a set of places based on a string — for example "pizza in New York" or "shoe stores near Ottawa" or "123 Main Street". The service responds with a list of places matching the text string and any location bias that has been set.

The service is especially useful for making ambiguous address queries in an automated system, and non-address components of the string may match businesses as well as addresses. Examples of ambiguous address queries are poorly-formatted addresses or requests that include non-address components such as business names. Requests like the first two examples in the following table may return zero results unless a location — such as region, location restriction, or location bias — is set.

"10 High Street, UK" or "123 Main Street, US"	Multiple "High Street"s in the UK; multiple "Main Street"s in the US. Query doesn't return desirable results unless a location restriction is set.  
"ChainRestaurant New York"	Multiple "ChainRestaurant" locations in New York; no street address or even street name.  
"10 High Street, Escher UK" or "123 Main Street, Pleasanton US"	Only one "High Street" in the UK city of Escher; only one "Main Street" in the US city of Pleasanton CA.  
"UniqueRestaurantName New York"	Only one establishment with this name in New York; no street address needed to differentiate.  
"pizza restaurants in New York"	This query contains its location restriction, and "pizza restaurants" is a well-defined place type. It returns multiple results.  
"+1 514-670-8700"	  
This query contains a phone number. It returns multiple results for places associated with that phone number.

Note: For best results when searching on a phone number, include the country code followed by a space, and set the regionCode parameter to correspond to the country code.  
The API Explorer lets you make live requests so that you can get familiar with the API and the API options:

Try it\!

Text Search requests  
A Text Search request is an HTTP POST request of the following form:

https://places.googleapis.com/v1/places:searchText  
Pass all parameters in the JSON request body or in headers as part of the POST request. For example:

curl \-X POST \-d '{  
  "textQuery" : "Spicy Vegetarian Food in Sydney, Australia"  
}' \\  
\-H 'Content-Type: application/json' \-H 'X-Goog-Api-Key: API\_KEY' \\  
\-H 'X-Goog-FieldMask: places.displayName,places.formattedAddress,places.priceLevel' \\  
'https://places.googleapis.com/v1/places:searchText'  
Text Search (New) responses  
Text Search (New) returns a JSON object as a response. In the response:

The places array contains all matching places.  
Each place in the array is represented by a Place object. The Place object contains detailed information about a single place.  
The FieldMask passed in the request specifies the list of fields returned in the Place object.  
The complete JSON object is in the form:

{  
  "places": \[  
    {  
      object (Place)  
    }  
  \]  
}  
Required parameters  
FieldMask  
Specify the list of fields to return in the response by creating a response field mask. Pass the response field mask to the method by using the URL parameter $fields or fields, or by using the HTTP header X-Goog-FieldMask. There is no default list of returned fields in the response. If you omit the field mask, the method returns an error.

Field masking is a good design practice to ensure that you don't request unnecessary data, which helps to avoid unnecessary processing time and billing charges.

Specify a comma-separated list of place data types to return. For example, to retrieve the display name and the address of the place.

X-Goog-FieldMask: places.displayName,places.formattedAddress  
Note: Spaces are not allowed anywhere in the field list.  
Use \* to retrieve all fields.

X-Goog-FieldMask: \*  
Wildcard "\*" selects all fields. However, while that wildcard is fine to use in development, Google discourage the use of the wildcard (\*) response field mask in production because of the large amount of data that can be returned.  
Further guidance for using places.iconMaskBaseUri and places.iconBackgroundColor can be found in Place Icons section.  
Specify one or more of the following fields:

The following fields trigger the Text Search (ID Only) SKU:

places.attributions, places.id, places.name\*, nextPageToken

\* The places.name field contains the place resource name in the form: places/PLACE\_ID. Use places.displayName to access the text name of the place.  
The following fields trigger the Text Search (Basic) SKU:

places.accessibilityOptions, places.addressComponents, places.adrFormatAddress, places.businessStatus, places.containingPlaces, places.displayName, places.formattedAddress, places.googleMapsLinks\*, places.googleMapsUri, places.iconBackgroundColor, places.iconMaskBaseUri, places.location, places.photos, places.plusCode, places.primaryType, places.primaryTypeDisplayName, places.pureServiceAreaBusiness, places.shortFormattedAddress, places.subDestinations, places.types, places.utcOffsetMinutes, places.viewport

\* The places.googleMapsLinks field is in the pre-GA Preview stage and there is no charge, meaning billing is $0, for usage during Preview.  
The following fields trigger the Text Search (Advanced) SKU:

places.currentOpeningHours, places.currentSecondaryOpeningHours, places.internationalPhoneNumber, places.nationalPhoneNumber, places.priceLevel, places.priceRange, places.rating, places.regularOpeningHours, places.regularSecondaryOpeningHours, places.userRatingCount, places.websiteUri  
The following fields trigger the Text Search (Preferred) SKU:

places.allowsDogs, places.curbsidePickup, places.delivery, places.dineIn, places.editorialSummary, places.evChargeOptions, places.fuelOptions, places.goodForChildren, places.goodForGroups, places.goodForWatchingSports, places.liveMusic, places.menuForChildren, places.parkingOptions, places.paymentOptions, places.outdoorSeating, places.reservable, places.restroom, places.reviews, places.routingSummaries,\* places.servesBeer, places.servesBreakfast, places.servesBrunch, places.servesCocktails, places.servesCoffee, places.servesDessert, places.servesDinner, places.servesLunch, places.servesVegetarianFood, places.servesWine, places.takeout

\* Text Search and Nearby Search only  
textQuery  
The text string on which to search, for example: "restaurant", "123 Main Street", or "best place to visit in San Francisco". The API returns candidate matches based on this string and orders the results based on their perceived relevance.

Optional parameters  
includedType  
Restricts the results to places matching the specified type defined by Table A. Only one type may be specified. For example:

"includedType":"bar"  
"includedType":"pharmacy"  
Note: The values in Table B are only returned in the response. You cannot use values in Table B as a filter.  
includePureServiceAreaBusinesses  
If set to true, the response includes businesses that visit or deliver to customers directly, but don't have a physical business location. If set to false, the API returns only businesses with a physical business location.

languageCode  
The language in which to return results.

See the list of supported languages. Google often updates the supported languages, so this list may not be exhaustive.  
If languageCode is not supplied, the API defaults to en. If you specify an invalid language code, the API returns an INVALID\_ARGUMENT error.  
The API does its best to provide a street address that is readable for both the user and locals. To achieve that goal, it returns street addresses in the local language, transliterated to a script readable by the user if necessary, observing the preferred language. All other addresses are returned in the preferred language. Address components are all returned in the same language, which is chosen from the first component.  
If a name is not available in the preferred language, the API uses the closest match.  
The preferred language has a small influence on the set of results that the API chooses to return, and the order in which they are returned. The geocoder interprets abbreviations differently depending on language, such as the abbreviations for street types, or synonyms that may be valid in one language but not in another.  
locationBias  
Specifies an area to search. This location serves as a bias which means results around the specified location can be returned, including results outside the specified area.

You can specify locationRestriction or locationBias, but not both. Think of locationRestriction as specifying the region which the results must be within, and locationBias as specifying the region that the results will likely be inside or near but can be outside of the area.

Note: If you omit both locationBias and locationRestriction, then the API uses IP biasing by default. With IP biasing, the API uses the device's IP address to bias the results.  
Note: The locationBias parameter can be overridden if the textQuery contains an explicit location such as Market in Barcelona. In this case, locationBias is ignored.  
Specify the region as a rectangular Viewport or as a circle.

A circle is defined by center point and radius in meters. The radius must be between 0.0 and 50000.0, inclusive. The default radius is 0.0. For example:

"locationBias": {  
  "circle": {  
    "center": {  
      "latitude": 37.7937,  
      "longitude": \-122.3965  
    },  
    "radius": 500.0  
  }  
}  
A rectangle is a latitude-longitude viewport, represented as two diagonally opposite low and high points. The low point marks the southwest corner of the rectangle, and the high point represents the northeast corner of the rectangle.

A viewport is considered a closed region, meaning it includes its boundary. The latitude bounds must range between \-90 to 90 degrees inclusive, and the longitude bounds must range between \-180 to 180 degrees inclusive:

If low \= high, the viewport consists of that single point.  
If low.longitude \> high.longitude, the longitude range is inverted (the viewport crosses the 180 degree longitude line).  
If low.longitude \= \-180 degrees and high.longitude \= 180 degrees, the viewport includes all longitudes.  
If low.longitude \= 180 degrees and high.longitude \= \-180 degrees, the longitude range is empty.  
If low.latitude \> high.latitude, the latitude range is empty.  
Both low and high must be populated, and the represented box cannot be empty. An empty viewport results in an error.

For example, this viewport fully encloses New York City:

"locationBias": {  
  "rectangle": {  
    "low": {  
      "latitude": 40.477398,  
      "longitude": \-74.259087  
    },  
    "high": {  
      "latitude": 40.91618,  
      "longitude": \-73.70018  
    }  
  }  
}  
locationRestriction  
Specifies an area to search. Results outside the specified area are not returned.

Specify the region as a rectangular Viewport. For an example of defining the Viewport, see the description of locationBias.

You can specify locationRestriction or locationBias, but not both. Think of locationRestriction as specifying the region which the results must be within, and locationBias as specifying the region that the results will likely be inside or near but can be outside of the area.

Note: If you omit both locationBias and locationRestriction, then the API uses IP biasing by default. With IP biasing, the API uses the IP address of the device to bias the results.  
maxResultCount (deprecated)  
Deprecated: This field is deprecated in favor of pageSize. If both maxResultCount and pageSize are specified, pageSize will be used and maxResultCount will be ignored.  
Specifies the number of results (between 1 and 20\) to display per page. For example, setting a maxResultCount value of 5 will return up to 5 results on the first page. If there are more results that can be returned from the query, the response includes a nextPageToken that you can pass into a subsequent request to access the next page.

Note: If maxResultCount is 0 or unspecified, the API will return 20 results per page by default. If maxResultCount is greater than 20, the API will return no more than 20 results per page.  
evOptions  
Specifies parameters for identifying available electric vehicle (EV) charging connectors and charging rates.

connectorTypes  
Filters by the type of EV charging connector available at a place. A place that does not support any of the connector types will be filtered out. Supported EV charging connector types include combined (AC and DC) chargers, Tesla chargers, GB/T-compliant chargers (for EV fast charging in China), and wall outlet chargers. For more information, see the reference documentation.

minimumChargingRateKw  
Filters places by minimum EV charging rate in kilowatts (kW). Any places with charging a rate less than the minimum charging rate are filtered out. For example, to find EV chargers with charging rates that are at least 10 kW, you can set this parameter to "10."

minRating  
Restricts results to only those whose average user rating is greater than or equal to this limit. Values must be between 0.0 and 5.0 (inclusive) in increments of 0.5. For example: 0, 0.5, 1.0, ... , 5.0 inclusive. Values are rounded up to the nearest 0.5. For example, a value of 0.6 eliminates all results with a rating less than 1.0.

openNow   
If true, return only those places that are open for business at the time the query is sent. If false, return all businesses regardless of open status. Places that don't specify opening hours in the Google Places database are returned if you set this parameter to false.

pageSize  
Specifies the number of results (between 1 and 20\) to display per page. For example, setting a pageSize value of 5 will return up to 5 results on the first page. If there are more results that can be returned from the query, the response includes a nextPageToken that you can pass into a subsequent request to access the next page.

Note: If pageSize is 0 or unspecified, the API will return 20 results per page by default. If pageSize is greater than 20, the API will return no more than 20 results per page.  
pageToken  
Specifies the nextPageToken from the response body of the previous page.

priceLevels  
Restrict the search to places that are marked at certain price levels. The default is to select all price levels.

Specify an array of one or more of values defined by PriceLevel.

Note: PRICE\_LEVEL\_FREE is not allowed in a request. It is only used to populate the response.  
For example:

"priceLevels":\["PRICE\_LEVEL\_INEXPENSIVE", "PRICE\_LEVEL\_MODERATE"\]  
rankPreference  
Specifies how the results are ranked in the response based on the type of query:

For a categorical query such as "Restaurants in New York City", RELEVANCE (rank results by search relevance) is the default. You can set rankPreference to RELEVANCE or DISTANCE (rank results by distance).  
For a non-categorical query such as "Mountain View, CA", we recommend that you leave rankPreference unset.  
regionCode  
The region code used to format the response, specified as a two-character CLDR code value. This parameter can also have a bias effect on the search results. There is no default value.

If the country name of the formattedAddress field in the response matches the regionCode, the country code is omitted from formattedAddress. This parameter has no effect on adrFormatAddress, which always includes the country name when available, or on shortFormattedAddress, which never includes it.

Most CLDR codes are identical to ISO 3166-1 codes, with some notable exceptions. For example, the United Kingdom's ccTLD is "uk" (.co.uk) while its ISO 3166-1 code is "gb" (technically for the entity of "The United Kingdom of Great Britain and Northern Ireland"). The parameter can affect results based on applicable law.

strictTypeFiltering  
Used with the includedType parameter. When set to true, only places that match the specified types specified by includeType are returned. When false, the default, the response can contain places that don't match the specified types.

Text Search examples  
Find a place by query string  
The following example shows a Text Search request for "Spicy Vegetarian Food in Sydney, Australia":

curl \-X POST \-d '{  
  "textQuery" : "Spicy Vegetarian Food in Sydney, Australia"  
}' \\  
\-H 'Content-Type: application/json' \-H 'X-Goog-Api-Key: API\_KEY' \\  
\-H 'X-Goog-FieldMask: places.displayName,places.formattedAddress' \\  
'https://places.googleapis.com/v1/places:searchText'  
Note that the X-Goog-FieldMask header specifies that the response contains the following data fields: places.displayName,places.formattedAddress. The response is then in the form:

{  
  "places": \[  
    {  
      "formattedAddress": "367 Pitt St, Sydney NSW 2000, Australia",  
      "displayName": {  
        "text": "Mother Chu's Vegetarian Kitchen",  
        "languageCode": "en"  
      }  
    },  
    {  
      "formattedAddress": "175 First Ave, Five Dock NSW 2046, Australia",  
      "displayName": {  
        "text": "Veggo Sizzle \- Vegan & Vegetarian Restaurant, Five Dock, Sydney",  
        "languageCode": "en"  
      }  
    },  
    {  
      "formattedAddress": "29 King St, Sydney NSW 2000, Australia",  
      "displayName": {  
        "text": "Peace Harmony",  
        "languageCode": "en"  
      }  
    },  
    ...  
  \]  
}  
Add more data types to the field mask to return additional information. For example, add places.types,places.websiteUri to include the restaurant type and Web address in the response:

curl \-X POST \-d '{  
  "textQuery" : "Spicy Vegetarian Food in Sydney, Australia"  
}' \\  
\-H 'Content-Type: application/json' \-H 'X-Goog-Api-Key: API\_KEY' \\  
\-H 'X-Goog-FieldMask: places.displayName,places.formattedAddress,places.types,places.websiteUri' \\  
'https://places.googleapis.com/v1/places:searchText'  
The response is now in the form:

{  
  "places": \[  
    {  
      "types": \[  
        "vegetarian\_restaurant",  
        "vegan\_restaurant",  
        "chinese\_restaurant",  
        "restaurant",  
        "food",  
        "point\_of\_interest",  
        "establishment"  
      \],  
      "formattedAddress": "367 Pitt St, Sydney NSW 2000, Australia",  
      "websiteUri": "http://www.motherchusvegetarian.com.au/",  
      "displayName": {  
        "text": "Mother Chu's Vegetarian Kitchen",  
        "languageCode": "en"  
      }  
    },  
    {  
      "types": \[  
        "vegan\_restaurant",  
        "thai\_restaurant",  
        "vegetarian\_restaurant",  
        "indian\_restaurant",  
        "italian\_restaurant",  
        "american\_restaurant",  
        "restaurant",  
        "food",  
        "point\_of\_interest",  
        "establishment"  
      \],  
      "formattedAddress": "175 First Ave, Five Dock NSW 2046, Australia",  
      "websiteUri": "http://www.veggosizzle.com.au/",  
      "displayName": {  
        "text": "Veggo Sizzle \- Vegan & Vegetarian Restaurant, Five Dock, Sydney",  
        "languageCode": "en"  
      }  
    },  
    ...  
  \]  
}  
Filter places by price level  
Use the priceLevel option to filter the results to restaurants defined as inexpensive or moderately expensive:

curl \-X POST \-d '{  
  "textQuery" : "Spicy Vegetarian Food in Sydney, Australia",  
  "priceLevels":\["PRICE\_LEVEL\_INEXPENSIVE", "PRICE\_LEVEL\_MODERATE"\]  
}' \\  
\-H 'Content-Type: application/json' \-H 'X-Goog-Api-Key: API\_KEY' \\  
\-H 'X-Goog-FieldMask: places.displayName,places.formattedAddress,places.priceLevel' \\  
'https://places.googleapis.com/v1/places:searchText'  
This example also uses the X-Goog-FieldMask header to add the places.priceLevel data field to the response so it is in the form:

{  
  "places": \[  
    {  
      "formattedAddress": "367 Pitt St, Sydney NSW 2000, Australia",  
      "priceLevel": "PRICE\_LEVEL\_MODERATE",  
      "displayName": {  
        "text": "Mother Chu's Vegetarian Kitchen",  
        "languageCode": "en"  
      }  
    },  
    {  
      "formattedAddress": "115 King St, Newtown NSW 2042, Australia",  
      "priceLevel": "PRICE\_LEVEL\_MODERATE",  
      "displayName": {  
        "text": "Green Mushroom",  
        "languageCode": "en"  
      }  
    },  
    ...  
  \]  
}  
Add additional options to refine your search, such as includedType, minRating, rankPreference, openNow, and other parameters described in Optional parameters.

Note: These refinement parameters only apply to queries such as "Restaurants in New York City" where the parameters help to reduce the number of search results based on the specified option. Applying these parameters to other type of queries—for example, to geographical queries such as "Mountain View, CA" or "New York City"—can actually result in filtering out meaningful results or reducing the number of meaningful results.  
Restrict search to a specified area  
Use locationRestriction or locationBias, but not both, to restrict a search to an area. Think of locationRestriction as specifying the region which the results must be within, and locationBias as specifying the region that the results must be near but can be outside of the area.

Note: When using locationRestriction, you can only specify the region as a rectangular Viewport. When using locationBias, you can specify the region as a rectangular Viewport or as a circle.  
Restrict area using locationRestriction  
Use the locationRestriction parameter to restrict query results to a specified region. In your request body, specify the low and high latitude and longitude values that define the region boundary.

The following example shows a Text Search request for "vegetarian food" in New York City. This request only returns the first 10 results for places that are open.

curl \-X POST \-d '{  
  "textQuery" : "vegetarian food",  
  "pageSize" : "10",  
  "locationRestriction": {  
    "rectangle": {  
      "low": {  
        "latitude": 40.477398,  
        "longitude": \-74.259087  
      },  
      "high": {  
        "latitude": 40.91618,  
        "longitude": \-73.70018  
      }  
    }  
  }  
}' \\  
  \-H 'Content-Type: application/json' \\  
  \-H 'X-Goog-Api-Key: API\_KEY' \\  
  \-H 'X-Goog-FieldMask: places.id,places.formattedAddress' \\  
  'https://places.googleapis.com/v1/places:searchText'  
Bias to an area using locationBias  
The following example shows a Text Search request for "vegetarian food" biased to a location within 500 meters of a point in downtown San Francisco. This request only returns the first 10 results for places that are open.

curl \-X POST \-d '{  
  "textQuery" : "vegetarian food",  
  "openNow": true,  
  "pageSize": 10,  
  "locationBias": {  
    "circle": {  
      "center": {"latitude": 37.7937, "longitude": \-122.3965},  
      "radius": 500.0  
    }  
  },  
}' \\  
\-H 'Content-Type: application/json' \-H 'X-Goog-Api-Key: API\_KEY' \\  
\-H 'X-Goog-FieldMask: places.displayName,places.formattedAddress' \\  
'https://places.googleapis.com/v1/places:searchText'  
Search for EV chargers with a minimum charging rate  
Use minimumChargingRateKw and connectorTypes to search for places with available chargers that are compatible with your EV.

The following example shows a request for Tesla and J1772 type 1 EV charging connectors with a minimum charging rate of 10 kW in Mountain View, CA. Only four results are returned.

curl \-X POST \-d '{  
    "textQuery": "EV Charging Station Mountain View",  
    "pageSize": 4,  
    "evOptions": {  
      "minimumChargingRateKw": 10,  
      "connectorTypes": \["EV\_CONNECTOR\_TYPE\_J1772","EV\_CONNECTOR\_TYPE\_TESLA"\]  
    }  
  }' \\  
\-H 'Content-Type: application/json' \-H 'X-Goog-Api-Key: API\_KEY' \\  
\-H "X-Goog-FieldMask: places.displayName,places.evChargeOptions" \\  
'https://places.googleapis.com/v1/places:searchText'  
The request returns the following response:

{  
  "places": \[  
    {  
      "displayName": {  
        "text": "EVgo Charging Station",  
        "languageCode": "en"  
      },  
      "evChargeOptions": {  
        "connectorCount": 16,  
        "connectorAggregation": \[  
          {  
            "type": "EV\_CONNECTOR\_TYPE\_CHADEMO",  
            "maxChargeRateKw": 100,  
            "count": 8,  
            "availableCount": 5,  
            "outOfServiceCount": 0,  
            "availabilityLastUpdateTime": "2024-01-10T19:10:00Z"  
          },  
          {  
            "type": "EV\_CONNECTOR\_TYPE\_CCS\_COMBO\_1",  
            "maxChargeRateKw": 100,  
            "count": 2,  
            "availableCount": 2,  
            "outOfServiceCount": 0,  
            "availabilityLastUpdateTime": "2024-01-10T19:10:00Z"  
          },  
          {  
            "type": "EV\_CONNECTOR\_TYPE\_CCS\_COMBO\_1",  
            "maxChargeRateKw": 350,  
            "count": 6,  
            "availableCount": 3,  
            "outOfServiceCount": 0,  
            "availabilityLastUpdateTime": "2024-01-10T19:10:00Z"  
          }  
        \]  
      }  
    },  
    {  
      "displayName": {  
        "text": "EVgo Charging Station",  
        "languageCode": "en"  
      },  
      "evChargeOptions": {  
        "connectorCount": 6,  
        "connectorAggregation": \[  
          {  
            "type": "EV\_CONNECTOR\_TYPE\_CCS\_COMBO\_1",  
            "maxChargeRateKw": 100,  
            "count": 4,  
            "availableCount": 3,  
            "outOfServiceCount": 0,  
            "availabilityLastUpdateTime": "2024-01-10T19:10:00Z"  
          },  
          {  
            "type": "EV\_CONNECTOR\_TYPE\_CCS\_COMBO\_1",  
            "maxChargeRateKw": 350,  
            "count": 2,  
            "availableCount": 0,  
            "outOfServiceCount": 2,  
            "availabilityLastUpdateTime": "2024-01-10T19:10:00Z"  
          }  
        \]  
      }  
    },  
    {  
      "displayName": {  
        "text": "EVgo Charging Station",  
        "languageCode": "en"  
      },  
      "evChargeOptions": {  
        "connectorCount": 5,  
        "connectorAggregation": \[  
          {  
            "type": "EV\_CONNECTOR\_TYPE\_J1772",  
            "maxChargeRateKw": 3.5999999046325684,  
            "count": 1,  
            "availableCount": 0,  
            "outOfServiceCount": 1,  
            "availabilityLastUpdateTime": "2024-01-10T19:10:00Z"  
          },  
          {  
            "type": "EV\_CONNECTOR\_TYPE\_CHADEMO",  
            "maxChargeRateKw": 50,  
            "count": 2,  
            "availableCount": 0,  
            "outOfServiceCount": 0,  
            "availabilityLastUpdateTime": "2024-01-10T19:10:00Z"  
          },  
          {  
            "type": "EV\_CONNECTOR\_TYPE\_CCS\_COMBO\_1",  
            "maxChargeRateKw": 50,  
            "count": 2,  
            "availableCount": 0,  
            "outOfServiceCount": 0,  
            "availabilityLastUpdateTime": "2024-01-10T19:10:00Z"  
          }  
        \]  
      }  
    },  
    {  
      "displayName": {  
        "text": "Electric Vehicle Charging Station",  
        "languageCode": "en"  
      },  
      "evChargeOptions": {  
        "connectorCount": 10,  
        "connectorAggregation": \[  
          {  
            "type": "EV\_CONNECTOR\_TYPE\_OTHER",  
            "maxChargeRateKw": 210,  
            "count": 10  
          }  
        \]  
      }  
    }  
  \]  
}  
Search for service area businesses  
Use the includePureServiceAreaBusinesses parameter to search for businesses without a physical service address (for example, a mobile cleaning service or a food truck).

The following example shows a request for plumbers in San Francisco:

curl \-X POST \-d '{  
  "textQuery" : "plumber San Francisco",  
  "includePureServiceAreaBusinesses": true  
}' \\  
\-H 'Content-Type: application/json' \-H 'X-Goog-Api-Key: API\_KEY' \\  
\-H 'X-Goog-FieldMask: places.displayName,places.formattedAddress' \\  
'https://places.googleapis.com/v1/places:searchText'  
In the response, businesses without a physical service address don't include the formattedAddress field:

{  
  "places": \[  
    {  
      "formattedAddress": "3450 Sacramento St \#204, San Francisco, CA 94118, USA",  
      "displayName": {  
        "text": "Advanced Plumbing & Drain",  
        "languageCode": "en"  
      }  
    },  
    {  
      "formattedAddress": "1455 Bancroft Ave, San Francisco, CA 94124, USA",  
      "displayName": {  
        "text": "Magic Plumbing Heating & Cooling",  
        "languageCode": "en"  
      }  
    },  
    /.../  
    {  
      "displayName": {  
        "text": "Starboy Plumbing Inc.",  
        "languageCode": "en"  
      }  
    },  
    {  
      "formattedAddress": "78 Dorman Ave, San Francisco, CA 94124, USA",  
      "displayName": {  
        "text": "Cabrillo Plumbing, Heating & Air",  
        "languageCode": "en"  
      }  
    },  
    {  
      "formattedAddress": "540 Barneveld Ave \# D, San Francisco, CA 94124, USA",  
      "displayName": {  
        "text": "Mr. Rooter Plumbing of San Francisco",  
        "languageCode": "en"  
      }  
    },  
    /.../  
    {  
      "displayName": {  
        "text": "Pipeline Plumbing",  
        "languageCode": "en"  
      }  
    },  
    {  
      "formattedAddress": "350 Bay St \#100-178, San Francisco, CA 94133, USA",  
      "displayName": {  
        "text": "One Source Plumbing and Rooter",  
        "languageCode": "en"  
      }  
    },  
    /.../  
  \]  
}  
Specify a number of results to return per page  
Use the pageSize parameter to specify a number of results to return per page. The nextPageToken parameter in the response body provides a token that can be used in subsequent calls to access the next page of results.

The following example shows a request for "pizza in New York" limited to 5 results per page:

 curl \-X POST \-d '{  
  "textQuery": "pizza in New York",  
  "pageSize": 5  
  }' \\  
\-H 'Content-Type: application/json' \-H 'X-Goog-Api-Key: API\_KEY' \\  
\-H "X-Goog-FieldMask: places.id,nextPageToken" \\  
'https://places.googleapis.com/v1/places:searchText'

{  
  "places": \[  
    {  
      "id": "ChIJifIePKtZwokRVZ-UdRGkZzs"  
    },  
    {  
      "id": "ChIJPxPd\_P1YwokRfzLhSiACEoU"  
    },  
    {  
      "id": "ChIJrXXKn5NZwokR78g0ipCnY60"  
    },  
    {  
      "id": "ChIJ6ySICVZYwokR9rIK8HjXhzE"  
    },  
    {  
      "id": "ChIJ6xvs94VZwokRnT1D2lX2OTw"  
    }  
  \],  
  "nextPageToken": "AeCrKXsZWzNVbPzO-MRWPu52jWO\_Xx8aKwOQ69\_Je3DxRpfdjClq8Ekwh3UcF2h2Jn75kL6PtWLGV4ecQri-GEUKN\_OFpJkdVc-JL4Q"  
}  
To access the next page of results, use pageToken to pass in the nextPageToken in the request body:

 curl \-X POST \-d '{  
  "textQuery": "pizza in New York",  
  "pageSize": 5,  
  "pageToken": "AeCrKXsZWzNVbPzO-MRWPu52jWO\_Xx8aKwOQ69\_Je3DxRpfdjClq8Ekwh3UcF2h2Jn75kL6PtWLGV4ecQri-GEUKN\_OFpJkdVc-JL4Q"  
  }' \\  
\-H 'Content-Type: application/json' \-H 'X-Goog-Api-Key: API\_KEY' \\  
\-H "X-Goog-FieldMask: places.id,nextPageToken" \\  
'https://places.googleapis.com/v1/places:searchText'

{  
  "places": \[  
    {  
      "id": "ChIJL-LN1N1ZwokR8K2jACu6Ydw"  
    },  
    {  
      "id": "ChIJjaD94kFZwokR-20CXqlpy\_4"  
    },  
    {  
      "id": "ChIJ6ffdpJNZwokRmcafdROM5q0"  
    },  
    {  
      "id": "ChIJ8Q2WSpJZwokRQz-bYYgEskM"  
    },  
    {  
      "id": "ChIJ8164qwFZwokRhplkmhvq1uE"  
    }  
  \],  
  "nextPageToken": "AeCrKXvPd6uUy-oj96W2OaqEe2pUD8QTxOM8-sKfUcFsC9t2Wey5qivrKGoGSxcZnyc7RPmaFfAktslrKbUh31ZDTkL0upRmaxA7c\_c"  
}  
Note: All parameters other than maxResultCount, pageSize, and pageToken must be the same as the previous request. Otherwise, the API returns an INVALID\_ARGUMENT error.  
Try it\!  
The API Explorer lets you make sample requests so that you can get familiar with the API and the API options.

Select the API icon, Expand the API Explorer., on the right side of the page.

Optionally expand Show standard parameters and set the fields parameter to the field mask.

Optionally edit the Request body.

Select Execute button. In the pop-up dialog box, choose the account that you want to use to make the request.

In the API Explorer panel, select the expand icon, Expand the API Explorer., to expand the API Explorer window.

\<google\_places\_v1\_documentation\>

| Toronto plumbers |
| :---- |
| Best plumbers in Toronto |
| Toronto electricians |
| Affordable electricians Toronto |
| Painters in Toronto |
| House painters Toronto |
| HVAC services Toronto |
| Roofing contractors Toronto |
| Toronto handymen |
| Home renovation Toronto |
| Home improvement Toronto |

| [Ajax](https://en.wikipedia.org/wiki/Ajax,_Ontario) | [Town](https://en.wikipedia.org/wiki/List_of_towns_in_Ontario) ([lower-tier](https://en.wikipedia.org/wiki/List_of_municipalities_in_Ontario#Lower-tier_municipalities)) |
| :---- | :---- |
| [Aurora](https://en.wikipedia.org/wiki/Aurora,_Ontario) | [Town](https://en.wikipedia.org/wiki/List_of_towns_in_Ontario) ([lower-tier](https://en.wikipedia.org/wiki/List_of_municipalities_in_Ontario#Lower-tier_municipalities)) |
| [Brampton](https://en.wikipedia.org/wiki/Brampton) | [City](https://en.wikipedia.org/wiki/List_of_cities_in_Ontario) ([lower-tier](https://en.wikipedia.org/wiki/List_of_municipalities_in_Ontario#Lower-tier_municipalities)) |
| [Brock](https://en.wikipedia.org/wiki/Brock,_Ontario) | [Township](https://en.wikipedia.org/wiki/List_of_township_municipalities_in_Ontario) ([lower-tier](https://en.wikipedia.org/wiki/List_of_municipalities_in_Ontario#Lower-tier_municipalities)) |
| [Burlington](https://en.wikipedia.org/wiki/Burlington,_Ontario) | [City](https://en.wikipedia.org/wiki/List_of_cities_in_Ontario) ([lower-tier](https://en.wikipedia.org/wiki/List_of_municipalities_in_Ontario#Lower-tier_municipalities)) |

I have two csv i created, what  i want to you to do is to create a directory website

The goal is to create an innovative online directory connecting homeowners and businesses in Toronto with verified trade workers, such as plumbers, painters, and electricians. The platform will combine features proven successful in existing competitor platforms with unique, localized value propositions to create a standout service.

### **Target Audience**

1. **Primary Users**:  
   * Homeowners and small businesses in Toronto are seeking professional trade workers.  
2. **Service Providers**:

Verified local trade workers (plumbers, painters, electricians, etc.) who want to expand their clientele.

 I want the directory website to use uses the   
\<google\_places\_v1\_documentation\> in order to display search results for these terms an example would be  “ plumber in brock toronto” make sure you always add the keyword toronto at the end of each keyword.

Then the websites should be generated programmatically, abusing the fact that Google tent to rank phrase-match pages with queries, so ensure that the meta title and meta description, title, and short content on the page mentions the exact phrase match keyword

Do not display images, display 10 result at a time, and create all pages programmatically using the two csvs above- use paginations as we are going to have alot of pages 

Create a sitemap, breadcrumbs, header, footer, and everything we need to have the site running efficiently

For the search bar only allow people to select terms from the csvs and not just search for stuff  
Create all index pages such as Best x in y, we won't do individual business pages yet

Use term such as “ Top 10 x in y city in Toronto” or “Best 7 x in y city in toronto” or “Best Affordable X service in toronto” or “Top Rated x in y city in toronto ”

Create  a clean looking ui/ux using modern modular block, taking in consideration contrast of color of  text vs background, and being mobile friendly throughout including header and hero session

Let's also create a mongo.db powered form to allow people to send submissions which will capture ans store the information/inquiry inside mongo.db capturing as much information as possible from the user

Make sure to use the a 6 month cache by storing the information found from googles api in mongo.db

