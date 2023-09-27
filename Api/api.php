<?php 
#får in alla classer
spl_autoload_register(function ($class) {
    include 'classes/' . $class . '.class.php';
});
if ($_SERVER["REQUEST_METHOD"]=="POST"){
    $do = $_POST["key1"];
    $ulr = $_POST["key2"];
    $data = $_POST["key3"];
    
    if ($do=="AddIgnore"){
        $sql = "INSERT INTO ignoretable (columns1) VALUES ('$ulr')";
        $classSql = new Sql;
        $stmt = $classSql->execute($sql); 

    }
    #koduprepning
    else if ($do =="AddVisited"){
        $sql = "INSERT INTO visited (columns1) VALUES ('$ulr')";
        $classSql = new Sql;
        $stmt = $classSql->execute($sql); 

    } 
    else if ($do =="AddContent"){
        $sql = "INSERT INTO content (columns1, columns2) VALUES ('$ulr', '$data')";
        $classSql = new Sql;
        $stmt = $classSql->execute($sql); 
        

    }
    
    #get function

    else if ($do =="GetVisited"){
        $sql = "SELECT * FROM visited";
        $classSql = new Sql;
        $stmt = $classSql->execute($sql); 
        while($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
           $arrayUlr[] = $row;  
        
        }
        $json = json_encode($arrayUlr);
        echo $json;
    }
    else if ($do =="GetIgnore"){
        $sql = "SELECT * FROM ignor";
        $classSql = new Sql;
        $stmt = $classSql->execute($sql); 
        while($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
           $arrayUlr[] = $row;  
        
        }
        $json = json_encode($arrayUlr);
        echo $json;
    }
    else if ($do =="GetContent"){
        $sql = "SELECT * FROM content";
        $classSql = new Sql;
        $stmt = $classSql->execute($sql); 
        while($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
           $array[] = $row;  
        
        }
        $json = json_encode($array);
        echo $json;
    }
}
