// DOM Strings go here
const DOMStrings = {
    "mask": "maskCount",
    "face": "faceCount",
    "totalFaceCount": "totalFaceCount",
    "totalMaskCount": "totalMaskCount",
    "totalRatio" : "totalRatio",
    "ratio": "ratio",
};

const url = "http://127.0.0.1:8000/surveillance/faceMaskMonitor/data";
if (typeof(EventSource) !== 'undefined') {
    // Create a new Event Source to make a SSE request
    const source = new EventSource(url);

    // DOM Elements
    faceCountDisplay = document.getElementById(DOMStrings.face);
    maskCountDisplay = document.getElementById(DOMStrings.mask);
    ratioDisplay = document.getElementById(DOMStrings.ratio);

    totalFaceCountDisplay = document.getElementById(DOMStrings.totalFaceCount);
    totalMaskCountDisplay = document.getElementById(DOMStrings.totalMaskCount);
    totalRatioDisplay = document.getElementById(DOMStrings.totalRatio);

    stream = document.querySelector("img");
    title = document.querySelector(".header .title");
    main = document.querySelector("main");

    setTimeout(function() {
        stream.src = "http://127.0.0.1:5001/"
    }, 5000)

    // Variables
    let counter = 0, totalFaceCount = 0, totalMaskCount = 0, totalRatio = '-';
    source.onmessage = (event) => {
        // Get data from server and parse as JSON
        const data = JSON.parse(event.data);

        faceCountDisplay.innerHTML = data.face_count;
        maskCountDisplay.innerHTML = data.mask_count;
        ratioDisplay.innerHTML = (data.ratio * 100).toFixed(1);

        // Find Total Stats for duration of 30 frames
        if (counter < 30) {
            totalFaceCount += data.face_count;
            totalMaskCount += data.mask_count;
            if (totalFaceCount > 0) {
                totalRatio = (totalMaskCount / totalFaceCount * 100).toFixed(1);
            } else {
                totalRatio = '-';
            }

            counter++;
        } else {
            // display the total counts
            totalFaceCountDisplay.innerHTML = totalFaceCount;
            totalMaskCountDisplay.innerHTML = totalMaskCount;
            totalRatioDisplay.innerHTML = totalRatio;

            // Reset for the next 30 frames
            totalMaskCount = 0;
            totalFaceCount = 0;
            totalRatio = '-';
            counter = 0;
        }

        // Hide the loading screen and set the display of title.
        main.classList.add("loaded");
        title.classList.add("title-loaded");

        // if (!videoPlayback) {
        //     video.play();
        //     video.playbackRate = 0.5;
        //     videoPlayback = true;
        // }
    }
    source.onopen = (event) => {
        console.log("Opened a SSE");
        console.log(event);
    }
    source.onerror = (event) => {
        console.log("[ERR] Error maintaining connection with SSE");
        console.log(event);
        console.log("Closing connection");
        source.close();
    }
}
