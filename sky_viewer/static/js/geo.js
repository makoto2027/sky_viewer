function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    } else {
        alert("このブラウザでは位置情報が取得できません。");
    }
}

function success(position) {
    // 都市名の結果を消す
    document.getElementById("weather-block").innerHTML = "";

    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    fetch(`/api/weather_by_coords?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(data => {
            if (data.都市) {
                document.getElementById("result").innerHTML = `
                    <h3>📍 ${data.都市}</h3>
                    <p>時刻：${data.時刻}</p>
                    <p>天気：${data.天気}</p>
                    <p>気温：${data.気温}</p>
                    <p>湿度：${data.湿度}</p>
                    <img src="http://openweathermap.org/img/wn/${data.アイコン}@2x.png">
                `;

                // お気に入り登録フォーム
                document.getElementById("favorite-form").innerHTML = `
                    <form method="post" action="/add_favorite">
                        <input type="hidden" name="city" value="${data.都市}">
                        <input type="hidden" name="weather" value="${data.天気}">
                        <input type="hidden" name="temperature" value="${data.気温}">
                        <input type="hidden" name="humidity" value="${data.湿度}">
                        <input type="hidden" name="icon" value="${data.アイコン}">
                        <input type="hidden" name="method" value="現在地">
                        <button type="submit">⭐ お気に入り登録</button>
                    </form>
                `;
            } else {
                document.getElementById("result").innerText = "天気情報を取得できませんでした。";
                document.getElementById("favorite-form").innerHTML = "";
            }
        });
}

function error() {
    alert("現在地の取得に失敗しました。");
}
