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


// 固定の都道府県リストの関数
function loadPrefectures() {
    const prefectures = [
        '北海道', '青森県', '岩手県', '宮城県', '秋田県',
        '山形県', '福島県', '茨城県', '栃木県', '群馬県',
        '埼玉県', '千葉県', '東京都', '神奈川県', '新潟県',
        '富山県', '石川県', '福井県', '山梨県', '長野県',
        '岐阜県', '静岡県', '愛知県', '三重県', '滋賀県',
        '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
        '鳥取県', '島根県', '岡山県', '広島県', '山口県',
        '徳島県', '香川県', '愛媛県', '高知県', '福岡県',
        '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県',
        '鹿児島県', '沖縄県'
    ];

    let prefectureSelect = document.getElementById('prefecture-select');
    prefectures.forEach(prefecture => {
        let option = document.createElement('option');
        option.value = prefecture;
        option.textContent = prefecture;
        prefectureSelect.appendChild(option);
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

