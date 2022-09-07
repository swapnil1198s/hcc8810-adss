import { Component, Suspense } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import LoadingAnimation from "./content/widgets/animatedLoader";

import 'bootstrap/dist/css/bootstrap.min.css';
import { Navbar } from 'react-bootstrap';
import "react-step-progress-bar/styles.css";
import './App.css';

import LandingPage from './content/pages/landing';
import RatingPage from './content/pages/ratemovies';
import RecommendationPage from './content/pages/raterecs';
import SizeWarningDialog from './content/widgets/sizewarnigdialog';

class RSSA extends Component {

	constructor(props) {
		super(props);
		this.state = {
			loaderActive: false,
			progress: 0
		};
		this.loaderToggler = this.toggleLoader.bind(this);
		this.progressUpdater = this.updateProgress.bind(this);
	}

	toggleLoader(toggle) {
		this.setState({
			loaderActive: toggle
		});
	}

	updateProgress(stepsize = 5) {
		let prog = this.state.progress + stepsize;

		this.setState({
			progress: prog > 100 ? 100 : prog
		});
	}

	render() {
		let loaderActive = this.state.loaderActive;
		let prog = this.state.progress;
		let progBarVisibility = loaderActive ? "pb_invisible" : "pb_visible";

		return (
			<div className="App">
				<Navbar id="topnav" bg="light">
					<Navbar.Brand style={{ marginLeft: "1em", fontWeight: "450" }}>RSSA</Navbar.Brand>
				</Navbar>
				<div className="contentWrapper">
					<SizeWarningDialog />
					<div style={{ margin: "0 3em" }}>
						<Router basename='/'>
							<Suspense fallback={<LoadingAnimation />}>
								<Routes>
									<Route path="/" element={<LandingPage dest="/preference" />} />
									<Route path="/preference" element={<RatingPage
										progressUpdater={this.progressUpdater} dest="/recommendations" />} />
									<Route path="/recommendations" element={<RecommendationPage
										progressUpdater={this.progressUpdater} toggleLoader={this.loaderToggler}
										waitMsg={"Please hang on while we find the recommendations for you."}
										pageHeader={"Refine your recommendations: Step 1 of 2"}
										headerSubtitle={"Please rate the following recommendations and alternative items to help us fine-tune our recommendations to you. Please rate all movies, even the ones you haven’t watched (read the description and then guess how you’d rate it.)"}
										finalhint={"Once you are done rating all the movies, click next to get a refined set of recommendations."}
										dest="/rssa/raterecommendations2" key={1} level={1} />}
									/>
								</Routes>
							</Suspense>
						</Router>
					</div>
				</div>
			</div>
		);
	}
}

export default RSSA;
