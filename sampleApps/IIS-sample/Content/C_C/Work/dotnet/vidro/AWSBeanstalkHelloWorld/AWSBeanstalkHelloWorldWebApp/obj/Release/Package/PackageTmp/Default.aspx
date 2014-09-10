<%@ Page Title="Home Page" Language="C#" MasterPageFile="~/Site.master" AutoEventWireup="true"
    CodeBehind="Default.aspx.cs" Inherits="AWSBeanstalkHelloWorldWebApp._Default" %>

<asp:Content ID="HeaderContent" runat="server" ContentPlaceHolderID="HeadContent">
</asp:Content>
<asp:Content ID="BodyContent" runat="server" ContentPlaceHolderID="MainContent">
	<section class="congratulations">
		<h1>Congratulations!</h1>
		<p>Your AWS Elastic Beanstalk <em>ASP.NET</em> application is now running on your own dedicated environment in the AWS&nbsp;Cloud</p>
	</section>
  
	<section class="instructions">
		<h2>What's Next?</h2>

    <ul>
        <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/">AWS Elastic Beanstalk overview</a></li>
        <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/index.html?concepts.html">AWS Elastic Beanstalk concepts</a></li>
        <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/create_deploy_NET.html">Deploying Applications in .NET Using AWS Toolkit for Visual Studio</a></li>
        <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/index.html?create_deploy_NET.container.html">Managing .NET Environment Settings </a></li>
        <li><a href="http://docs.amazonwebservices.com/elasticbeanstalk/latest/dg/using-features.loggingS3.title.html">Working with Logs </a></li>

    </ul>
    <h2>AWS SDK for .NET</h2>
    <ul>
			<li><a href="http://aws.amazon.com/sdkfornet/">AWS SDK for .NET home</a></li>
            <li><a href="http://aws.amazon.com/visualstudio/">AWS Toolkit for Visual Studio home</a></li>
			<li><a href="http://aws.amazon.com/net">Windows and .NET developer center</a></li>
			<li><a href="http://aws.amazon.com/documentation/sdkfornet">AWS SDK for .NET documentation</a></li>
			<li><a href="https://github.com/amazonwebservices/aws-sdk-for-net">AWS SDK for .NET on GitHub</a></li>
    </ul>
    <h2>Application Information</h2>
    <ul>
      <li><a href="Environment.aspx">View this applications AWS Elastic Beanstalk environment properties</a></li>
    </ul>
	</section>
</asp:Content>
