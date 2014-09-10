<%@ Page Title="" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="Environment.aspx.cs" Inherits="AWSBeanstalkHelloWorldWebApp.Envronment" %>
<asp:Content ID="Content1" ContentPlaceHolderID="HeadContent" runat="server">
</asp:Content>
<asp:Content ID="Content2" ContentPlaceHolderID="MainContent" runat="server">
	<section class="congratulations">
		<h1>Congratulations!</h1>
		<p>Your AWS Elastic Beanstalk <em>ASP.NET</em> application is now running on your own dedicated environment in the AWS&nbsp;Cloud</p>
	</section>
  
	<section class="instructions">
    <h1>AWS Elastic Beanstalk Environment Properties</h1>
    <p>Properties that are exposed through AWS Elastic Beanstalk and are available to your application</p>
  
  
    <h2>Environment Properties</h2>
    <ul id="Vars" runat="server">
    </ul>
    <h2>Links</h2>
    <ul>
      <li><a href="Default.aspx">Return to the Application home page.</a></li>
    </ul>
   </section>
  </asp:Content>
