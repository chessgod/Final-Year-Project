const slider = document.getElementById("clipSlider");
const value = document.getElementById("clipValue");


value.innerHTML = slider.value;

slider.oninput = function() {
  value.innerHTML = this.value;
}

function videoName() {
  var x = document.getElementById('videoInput')
  x.style.visibility = 'collapse'
  document.getElementById('videoName').innerHTML = x.value.split('\\').pop()
}

function gpxName() {
  var x = document.getElementById('gpxInput')
  x.style.visibility = 'collapse'
  document.getElementById('gpxName').innerHTML = x.value.split('\\').pop()
}


