<?
if ($_SERVER['REQUEST_METHOD'] === 'POST')
{
  $file = '/tmp/sample-app.log';
  $message = file_get_contents('php://input');
  file_put_contents($file, $message . "\n", FILE_APPEND);
}
else
{
?>
<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
	<title>PHP Application - AWS Elastic Beanstalk</title>
	<meta name="viewport" content="width=device-width">
	<link rel="stylesheet" href="http://fonts.googleapis.com/css?family=Lobster+Two" type="text/css">
	<link rel="icon" href="https://awsmedia.s3.amazonaws.com/favicon.ico" type="image/ico" >
	<link rel="shortcut icon" href="https://awsmedia.s3.amazonaws.com/favicon.ico" type="image/ico" >
	<!--[if IE]><script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script><![endif]-->
	<link rel="stylesheet" href="/styles.css" type="text/css">
</head>
<body>
	<section class="congratulations">
		<h1>Congratulations!</h1>
		<p>Your AWS Elastic Beanstalk <em>PHP</em> application is now running on your own dedicated environment in the AWS&nbsp;Cloud</p>
		<p>You are running PHP version <?php echo phpversion(); ?></p>
		<aside>(&nbsp;<a href="/info.php">View PHP information</a>&nbsp;)</aside>
	</section>

	<section class="instructions">
		<h2>What's Next?</h2>
		<ul>
			<li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/">AWS Elastic Beanstalk overview</a></li>
<li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/index.html?concepts.html">AWS Elastic Beanstalk concepts</a></li>
<li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/create_deploy_PHP.html">Deploying Applications in PHP Using Git</a></li>
<li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/index.html?create_deploy_PHP.container.html">Managing PHP Environment Settings </a></li>
<li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/using-features.loggingS3.title.html">Working with Logs </a></li>
		</ul>

		<h2>AWS SDK for PHP</h2>
		<ul>
			<li><a href="http://aws.amazon.com/sdkforphp">AWS SDK for PHP home</a></li>
			<li><a href="http://aws.amazon.com/php">PHP developer center</a></li>
			<li><a href="http://aws.amazon.com/articles/4261?_encoding=UTF8&jiveRedirect=1">Getting started guide</a></li>
			<li><a href="http://aws.amazon.com/documentation/sdkforphp">AWS SDK for PHP documentation</a></li>
			<li><a href="https://github.com/amazonwebservices/aws-sdk-for-php">AWS SDK for PHP on GitHub</a></li>
		</ul>
	</section>

	<!--[if lt IE 9]><script src="http://css3-mediaqueries-js.googlecode.com/svn/trunk/css3-mediaqueries.js"></script><![endif]-->
</body>
</html>
<? 
} 
?>