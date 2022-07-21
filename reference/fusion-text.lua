{
	Tools = ordered() {
		Background1 = Background {
			Inputs = {
				Width = Input { Value = 1920, },
				Height = Input { Value = 1080, },
			},
		}
	},
	ActiveTool = "Background1"
}


{
	Tools = ordered() {
		Background1 = Background {
			Inputs = {
				Width = Input { Value = 1920, },
				Height = Input { Value = 1080, },
			},
			ViewInfo = OperatorInfo { Pos = { 55, 49.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				Background = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 165, 49.5 } }, --added 110 to x pos
		}
	}
}


{
	Tools = ordered() {
		Background2 = Background {
			CtrlWZoom = false,
			Inputs = {
				GlobalOut = Input { Value = 100, },
				Width = Input { Value = 1920, },
				Height = Input { Value = 1080, },
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 110, -16.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				Background = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "Background2",
					Source = "Output",
				},
			},
			ViewInfo = OperatorInfo { Pos = { 110, 16.5 } },
		},
		Background1 = Background {
			Inputs = {
				GlobalOut = Input { Value = 100, },
				Width = Input { Value = 1920, },
				Height = Input { Value = 1080, },
			},
			ViewInfo = OperatorInfo { Pos = { 0, 16.5 } },
		}
	}
}


{
	Tools = ordered() {
		Loader1 = Loader {
			Clips = {
			},
			CtrlWZoom = false,
			Inputs = {
				["Gamut.SLogVersion"] = Input { Value = FuID { "SLog2" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 0, 16.5 } },
		},
		Merge1 = Merge {
			Inputs = {
				Background = Input {
					SourceOp = "Background1",
					Source = "Output",
				},
				Foreground = Input {
					SourceOp = "Loader1",
					Source = "Output",
				},
				EffectMask = Input {
					SourceOp = "Rectangle1",
					Source = "Mask",
				}
			},
			ViewInfo = OperatorInfo { Pos = { 110, 16.5 } },
		},
		
		Rectangle1 = RectangleMask {
			Inputs = {
				Filter = Input { Value = FuID { "Fast Gaussian" }, },
				MaskWidth = Input { Value = 1920, },
				MaskHeight = Input { Value = 1080, },
				PixelAspect = Input { Value = { 1, 1 }, },
				ClippingMode = Input { Value = FuID { "None" }, },
			},
			ViewInfo = OperatorInfo { Pos = { 220, 16.5 } },
		},
		Background1 = Background {
			Inputs = {
				GlobalOut = Input { Value = 100, },
				Width = Input { Value = 1920, },
				Height = Input { Value = 1080, },
			},
			ViewInfo = OperatorInfo { Pos = { 110, -16.5 } },
		}
	}
}