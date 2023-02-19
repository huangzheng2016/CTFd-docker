<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EASY WEB</title>
</head>
<body>
<p>Nothing Here</p>
<?php
$gg = $_GET['gg'];
echo base64_encode($gg);
$str = 'flag';

if($gg == base64_encode($str)){
    echo '<br>';
    highlight_string(
    '$GG = $_POST['.'GG'.'];
    echo $GG;
    if($GG == '.'flag'.')
        echo '.'flag{xxxxxxxx}'.';');
}

$GG = $_POST['GG'];
echo $GG;
if($GG == 'flag')
    echo file_get_contents('./fl0g');
?>
</body>
</html>