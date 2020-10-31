$(function() {
    /**
     * Функция делает высоту фреймов 
     * для загрузки картинки равной ширине
     */
    function resize_boxes() {
        $('.upload_container').height( 
            $('.upload_container').width() 
        );
    }

    /**
     * Функция срабатывает при изменении
     * размера окна браузера
     */
    $(window).resize(function() {
        console.log('Window resized');

        // Изменяем высоту фреймов
        resize_boxes();
    });

    $(document).ready(function() {
        // Очищаем все get параметры из URL
        window.history.replaceState({}, document.title, "/");

        // Вызываем событие resize чтобы вызвать resize_boxes
        $(window).trigger('resize');
    });
});