#!/usr/bin/perl -w

use CGI qw(:standard);
use GD::Graph::hbars;
use GD::Graph::pie;
use GD::Graph::colour qw(:files);
use GD::Text;
use strict;

print header();

sub draw_chart {
	my $mygraph = GD::Graph::hbars->new(1200,500);

        GD::Graph::colour::read_rgb( "/usr/X11R6/lib/X11/rgb.txt" ) or die( "Can't read colours" );

        $mygraph->set(

        x_label         => 'month',
        y_label         => 'Status Stats',
 #       title           => $title,
#        y_min_value     => $min,
#        y_max_value     => $max,
        y_tick_number   => 1,
        y_label_skip    => 2,
        x_label_skip    => 1,
        y_long_ticks    => 1,
        bar_spacing     => 1,
       long_ticks      => 1,
        cumulate        => 1,
#        boxclr       => "LightSkyBlue2",
#        dclrs        => [ "DarkSlateGray" ],
#        line_width      => 3,
       marker_size     => 2,
       markers         => [8],
       transparent     => 0,
        ) or warn $mygraph->error;

        $mygraph->set_legend( "Switching Time");
        GD::Text->font_path( "/usr/lib/X11/fonts/TTF/" );
        $mygraph->set_title_font( '/usr/lib/X11/fonts/TTF/luximr.ttf', 18 );
        $mygraph->set_legend_font( "/usr/lib/X11/fonts/TTF/luximr.ttf", 20 );
        $mygraph->set_x_axis_font( "luximr", 9 );
        $mygraph->set_x_label_font( "luximr", 11 );
        $mygraph->set_y_axis_font( "luximr", 9 );
        $mygraph->set_y_label_font( "luximr", 11 );
	
	return $mygraph;
}

my @data = (["10/25", "10/26", "10/27"],
		[12,14,10],
		[20,2,10],
		[10,10,5],
		[12,2,15],
		[22,3,3]
		);


my $chart = draw_chart();

my $my_image = $chart->plot(\@data);

createImage("hbar.gif", $my_image);

sub createImage {
        my $fileName  = shift;
        my $image_obj = shift;

        open IMG, ">$fileName" or die "$!:$fileName\n";
        binmode IMG;
        print IMG $image_obj->gif;
        close IMG;
}

