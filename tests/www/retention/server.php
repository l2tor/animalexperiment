<?php

$command = $_POST['command'];

if ($command == 'newlog') {
	// Create new log file
	$files = glob('logs/retention_log_*.txt');
	$maxfile = $files[count($files)-1];
	$success = sscanf($maxfile, 'logs/retention_log_%d.txt', $number);

	if (!$success)
		$number = 0;

	$myFile = "logs/retention_log_" . ($number+1) . ".txt";
	$fh = fopen($myFile, 'a') or die("can't open file");
	$stringData =$_POST['logcontent'] ;
	fwrite($fh, date('m/d/Y H:i:s', time()) . " ========== Retention test started\r\n");
	fclose($fh);	
}

else {
	// Write to log
	// Find highest log file number
	$files = glob('logs/retention_log_*.txt');
	$maxfile = $files[count($files)-1];
	$success = sscanf($maxfile, 'logs/retention_log_%d.txt', $number);

	$myFile = "logs/retention_log_" . ($number) . ".txt";
	$fh = fopen($myFile, 'a') or die("can't open file");
	$stringData =$_POST['logcontent'] ;
	fwrite($fh, date('m/d/Y H:i:s', time()) . ' ' . $stringData . "\r\n");
	fclose($fh);
}

?>