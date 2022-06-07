gothere.load("maps");
        function initialize() {
            if (GBrowserIsCompatible()) {
                // Create the Gothere map object.
            	var map = new GMap2(document.getElementById("map"));
            	// Set the center of the map.
            	map.setCenter(new GLatLng(1.29297, 103.8523), 16);
            	// Add zoom controls on the top left of the map.
            	map.addControl(new GSmallMapControl());
            	// Add a scale bar at the bottom left of the map.
            	map.addControl(new GScaleControl());
              }
        }
        gothere.setOnLoadCallback(initialize);