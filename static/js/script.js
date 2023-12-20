document.addEventListener('DOMContentLoaded', function() {
    // 初期化時に都道府県リストをロード
    loadPrefectures();

    // 都道府県が選択されたら市区町村リストを更新
    document.getElementById('prefecture-select').addEventListener('change', function() {
        let selectedPrefecture = this.value;
        loadMunicipalities(selectedPrefecture);
    });

    // ロードするボタンがクリックされたら団体コードを表示
    document.getElementById('load-button').addEventListener('click', function() {
        let selectedPrefecture = document.getElementById('prefecture-select').value;
        let selectedMunicipality = document.getElementById('municipality-select').value;
        displayGovCode(selectedPrefecture, selectedMunicipality);
    });
});

// Foliumマップのポップアップ内のボタンのスクリプト
function setFormData(pop_uuid, pop_date) {
    // 日付フィールドの値をセットする
    document.getElementById('date').value = pop_date;
    // 畑IDフィールドの値をセットする
    document.getElementById('uuid').value = pop_uuid;
}


// 都道府県リストをロードする関数
function loadPrefectures() {
    fetch('/get_local_gov_data')
    .then(response => response.json())
    .then(data => {
        let prefectureSelect = document.getElementById('prefecture-select');
        data.forEach(item => {
            let option = document.createElement('option');
            option.value = item['都道府県名\n（漢字）'];
            option.textContent = item['都道府県名\n（漢字）'];
            prefectureSelect.appendChild(option);
        });
    });
}

// 市区町村リストをロードする関数
function loadMunicipalities(prefecture) {
    fetch('/get_local_gov_data')
    .then(response => response.json())
    .then(data => {
        let municipalitySelect = document.getElementById('municipality-select');
        municipalitySelect.innerHTML = ''; // リストをクリア
        data.forEach(item => {
            if (item['都道府県名\n（漢字）'] === prefecture) {
                let option = document.createElement('option');
                option.value = item['市区町村名\n（漢字）'];
                option.textContent = item['市区町村名\n（漢字）'];
                municipalitySelect.appendChild(option);
            }
        });
    });
}

// 団体コードを表示する関数
function displayGovCode(prefecture, municipality) {
    fetch(`/get_gov_code?prefecture=${prefecture}&municipality=${municipality}`)
    .then(response => response.json())
    .then(data => {
        document.getElementById('gov-code').textContent = data['団体コード'];
    });
}

