const MINIMUM_SCORE = 0;
const MAXIMUM_SCORE = 20;
const EDITABLE_SCORE_INPUT_WIDTH = "80px";

function showEditButton(id){
    $(`#edit-${id}`).show();
}

function hideEditButton(id){
    $(`#edit-${id}`).hide();
}

function editScore(e){
    data = e.dataset.period ? extractPeriodScoreData(e.dataset) : extractEvolutionScoreData(e.dataset);
    showEditableScore(e, data);
    return false;
}

function extractPeriodScoreData(dataset) {
    return {
        student: dataset.student,
        period: dataset.period,
        computed: dataset.computed,
    };
}

function extractEvolutionScoreData(dataset) {
    return {
        student: dataset.student,
        scores: $(`#evolution_score_${dataset.student}`).data('scores'),
        computed: dataset.computed,
    };
}

function showEditableScore(e, data) {
    let cell = $(e).closest('td')[0];
    let formGroup = buildEditableScore(cell, data);
    cell.innerHTML = "";
    cell.append(formGroup);
}

function buildEditableScore(cell, data) {
    adaptPadding(cell);
    let oldCellContent = cell.innerHTML;
    const score_value = cell.innerText;
    let input = buildScoreInput(score_value);
    let formGroup = buildScoreFormGroup(input);
    let groupButton = buildScoreGroupButton(input, cell, oldCellContent, data);
    formGroup.append(groupButton);
    return formGroup;
}

function buildScoreInput(score_value) {
    let input = document.createElement("input");
    Object.assign(input, {
        value: parseInt(score_value),
        type: 'number',
        step: 1,
        min: MINIMUM_SCORE,
        max: MAXIMUM_SCORE
    });
    input.style.width = EDITABLE_SCORE_INPUT_WIDTH;
    input.classList.add("form-control");
    return input;
}

function buildScoreFormGroup(input) {
    let formGroup = document.createElement("div");
    formGroup.classList.add("input-group", "input-group-sm");
    formGroup.append(input);
    return formGroup;
}

function buildGroupButton() {
    let groupButton = document.createElement("span");
    groupButton.classList.add("input-group-btn");
    return groupButton;
}

function buildConfirmButton(input, cell, data) {
    let confirmButton = document.createElement("button");
    confirmButton.innerHTML = "<icon class='fas fa-check'><icon/>";
    confirmButton.classList.add("btn", "btn-primary");
    confirmButton.addEventListener('click', () => {
        data['edited'] = input.value;
        saveScore(data, cell);
    });
    return confirmButton;
}

function buildCancelButton(cell, oldCellContent) {
    let cancelButton = document.createElement("button");
    cancelButton.innerHTML = "<icon class='fas fa-times'><icon/>";
    cancelButton.classList.add("btn", "btn-secondary");
    cancelButton.addEventListener('click', () => {
        cell.innerHTML = oldCellContent;
        resetPadding(cell);
    });
    return cancelButton;
}

function buildScoreGroupButton(input, cell, oldCellContent, data) {
    let groupButton = buildGroupButton();
    let confirmButton = buildConfirmButton(input, cell, data);
    let cancelButton = buildCancelButton(cell, oldCellContent);
    groupButton.append(confirmButton);
    groupButton.append(cancelButton);
    return groupButton;
}

function adaptPadding(cell) {
    let paddingTop = parseInt($(cell).css('padding')) / 2 - 1;
    $(cell).css('padding', paddingTop + 'px 0px 0px 0px');
}

function resetPadding(cell){
    $(cell).css('padding', '');
}

function saveScore(data, cell) {
    if(data.edited % 1 === 0){
        if(data.period){
            savePeriodScore(data, cell);
        } else {
            saveEvolutionScore(data, cell);
        }
    } else {
        showErrorTooltip(cell, data);
    }
}

function deleteScore(e){
    let dataset = $(e).data();
    let data = dataset.period ? extractPeriodScoreData(dataset) : extractEvolutionScoreData(dataset);
    if(dataset.period){
        deletePeriodScore(data, dataset.cell);
        delete dataset.period;
    } else {
        deleteEvolutionScore(data, dataset.cell);
    }
}

//append data to modal button on modal open
$(document).on('click', '[data-target="#delete_score"]', function(){
    let deleteScoreBtn = $("#delete_score_btn");
    deleteScoreBtn.data(this.dataset);
    deleteScoreBtn.data("cell", $(this).closest('td')[0]);
    return false;
});

//AJAX LOGIC GOES HERE

function savePeriodScore(data, cell){
    $.ajax({
        url: "ajax/save_score/",
        method: "POST",
        data: data,
        success: response => {
            cell.innerHTML = response;
            resetPadding(cell);
            refreshEvolutionScore(data);
        },
        error: data => {
            showErrorTooltip(cell, data);
        }
    });
}

function saveEvolutionScore(data, cell){
    $.ajax({
        url: "ajax/save_evolution_score/",
        method: "POST",
        data: data,
        success: response => {
            cell.closest('tr').innerHTML = response;
        },
        error: data => {
            showErrorTooltip(cell, data);
        }
    });
}


function deletePeriodScore(data, cell){
    $.ajax({
        url: "ajax/delete_score/",
        method: "POST",
        data: data,
        success: response => {
            cell.innerHTML = response;
            refreshEvolutionScore(data);
        },
        error: error_data => showErrorTooltip(cell, error_data)
    });
}

function deleteEvolutionScore(data, cell){
    $.ajax({
        url: "ajax/delete_evolution_score/",
        method: "POST",
        data: data,
        success: response => cell.closest('tr').innerHTML = response,
        error: data => showErrorTooltip(cell, data)
    });
}

function showErrorTooltip(cell, data) {
    let inputGroup = $(cell).find(".input-group")[0];
    inputGroup.classList.add("has-error");
    inputGroup.setAttribute("data-toggle", "tooltip");
    inputGroup.setAttribute("data-placement", "top");
    if(data.responseJSON && data.responseJSON.error)
        inputGroup.setAttribute("title", data.responseJSON.error);
    $(inputGroup).tooltip('show');
}

function refreshEvolutionScore(data){
    let score_element = $(`#evolution_score_${data.student}`);
    let score_info_element = $(`#evolution_score_info_${data.student}`);
    data.scores = score_element.data('scores');
    $.ajax({
        url: "ajax/refresh_evolution_score/",
        method: "POST",
        data: data,
        success: response => buildAndReplaceEvolutionScore(response, score_element, score_info_element)
    })
}

function buildAndReplaceEvolutionScore(response, score_element, score_info_element) {
    let evolution_score = response['evolution_score'];
    score_element.data('scores', response['updated_scores']);
    if (!score_element.data('edited')) {
        score_element[0].innerHTML = evolution_score;
    } else {
        score_info_element.attr('title', response['computed_title_text'] + evolution_score);
    }
}