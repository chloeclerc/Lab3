function getCookie(c_name) {
  var i, x, y, ARRcookies = document.cookie.split(";");
  for (i = 0; i < ARRcookies.length; i++) {
    x = ARRcookies[i].substr(0, ARRcookies[i].indexOf("="));
    y = ARRcookies[i].substr(ARRcookies[i].indexOf("=") + 1);
    x = x.replace(/^\s+|\s+$/g, "");
    if (x == c_name) {
      return unescape(y);
    }
  }
}

function setCookie(c_name, value, exdays) {
  var exdate = new Date();
  exdate.setDate(exdate.getDate() + exdays);
  var c_value = escape(value) + ((exdays == null) ? "" : "; expires=" + exdate.toUTCString());
  document.cookie = c_name + "=" + c_value + "; path=/";
}

function checkForm(form) {
  var city = (form.elements["city"].value || "").trim();
  var state = (form.elements["state"].value || "").trim();

  if (city === "" && state === "") {
    alert("Please enter at least a state (or both city and state) to search.");
    return false;
  }

  var combined = (city + " " + state).trim().toLowerCase();
  var cityOnly = city.toLowerCase();
  if (combined === "elon musk" || cityOnly === "elon musk") {
    alert("He's not here");
    return false;
  }

  return true;
}

// 3b: first-visit cookie
(function firstVisitRedirect() {
  var cookieName = "handirides_visited";
  var hasVisited = getCookie(cookieName);
  var path = window.location.pathname;

  // Don't redirect if we're already on the splash page
  if (!hasVisited && path !== "/") {
    // mark as visited for 30 days
    setCookie(cookieName, "1", 30);

    // redirect to splash page
    window.location.href = "/";
  }
})();
(function priceEstimator() {
  // 1) City -> coordinates (extend this with your fixture cities)
  // Coordinates are approximate and totally fine for a class project.
  var coords = {
    "Princeton": [40.3573, -74.6672],
    "Newark": [40.7357, -74.1724],
    "Jersey City": [40.7178, -74.0431],
    "Edison": [40.5187, -74.4121],
    "Elizabeth": [40.6630, -74.2107],
    "Clark": [40.6270, -74.3132],
    "New York": [40.7128, -74.0060],
    "Washington": [38.9072, -77.0369]
  };

  // 2) Pricing model constants (tweakable)
  var BASE_FEE = 2.50;
  var RATE_PER_MILE = 0.85;
  var RATE_PER_MIN = 0.20;
  var AVG_SPEED_MPH = 35; // for time estimate

  function toRad(deg) {
    return deg * Math.PI / 180;
  }

  // 3) Haversine distance in miles
  function haversineMiles(a, b) {
    var lat1 = toRad(a[0]), lon1 = toRad(a[1]);
    var lat2 = toRad(b[0]), lon2 = toRad(b[1]);

    var dLat = lat2 - lat1;
    var dLon = lon2 - lon1;

    var s =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1) * Math.cos(lat2) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);

    var c = 2 * Math.atan2(Math.sqrt(s), Math.sqrt(1 - s));
    var earthRadiusMiles = 3958.8;
    return earthRadiusMiles * c;
  }

  function normalizeCityName(name) {
    return (name || "").trim();
  }

  function estimateTrip(originCity, destCity) {
    originCity = normalizeCityName(originCity);
    destCity = normalizeCityName(destCity);

    var a = coords[originCity];
    var b = coords[destCity];

    // fallback: if we don't have coords, return null
    if (!a || !b) return null;

    var miles = haversineMiles(a, b);

    // time estimate
    var minutes = (miles / AVG_SPEED_MPH) * 60;

    // cost estimate
    var cost = BASE_FEE + (miles * RATE_PER_MILE) + (minutes * RATE_PER_MIN);

    return { miles: miles, minutes: minutes, cost: cost };
  }

  function formatMoney(x) {
    return "$" + x.toFixed(2);
  }

  function clamp(n, lo, hi) {
    return Math.max(lo, Math.min(hi, n));
  }

  // 4) Apply to results table rows
  var rows = document.querySelectorAll("tr[data-origin][data-dest]");
  if (!rows.length) return;

  rows.forEach(function (row) {
    var origin = row.getAttribute("data-origin");
    var dest = row.getAttribute("data-dest");
    var seats = parseInt(row.getAttribute("data-seats") || "0", 10);
    var driver = (row.getAttribute("data-driver") || "").toLowerCase() === "true";

    var trip = estimateTrip(origin, dest);
    var cell = row.querySelector(".price-cell");
    if (!cell) return;

    if (!trip) {
      // If we can't compute distance, show placeholder
      cell.textContent = "N/A";
      cell.title = "No coordinates for " + origin + " or " + dest;
      return;
    }

    // group size assumption: driver + up to available seats
    // cap seats so it doesn't get weird if fixtures are huge
    var passengers = driver ? clamp(seats, 0, 6) : 0;
    var groupSize = 1 + passengers;

    var perPerson = trip.cost / groupSize;

    cell.textContent = formatMoney(perPerson);
    cell.title =
      "Trip est: " +
      trip.miles.toFixed(1) + " mi, " +
      Math.round(trip.minutes) + " min. " +
      "Total " + formatMoney(trip.cost) +
      " split among " + groupSize;
  });
})();