<?php
/**
 * class Sql
 * responsibility for sql quarys
 * @author jakob Hallin
 */
class Sql{
    /**
     * prepares and execute sql quaries
     * @return $stmt 
     */
	public function execute($sql){
			//$con = $this->con;
			$db = new Db;
			$con = $db->connect();
			$stmt = $con->prepare($sql);
			$stmt ->execute();
			return $stmt;
	}	
		
	/**
     * prepares and execute sql quaries to statment to insert
     */
	public function insert($sql, $arg1, $arg2){
		$db = new Db;
		$con = $db->connect();
        $stmt = $con->prepare($sql);
        $stmt->execute([$arg1, $arg2]);
	}
}
