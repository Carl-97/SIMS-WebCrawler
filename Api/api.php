<php 
spl_autoload_register(function ($class) {
    include 'classes/' . $class . '.class.php';
});
if ($_SERVER["REQUEST_METHOD"]=="POST"){

}